import json
import google.generativeai as genai
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async
from .ai_tools import _db_get_tickets, _db_get_projects

class SupportAIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        await self.accept()
        
        # Initialize Gemini
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # --- Define User-Bound Tools ---
            def get_my_tickets():
                """Fetch the list of my recent support tickets and their status."""
                return _db_get_tickets(self.user)

            def get_my_projects():
                """List the shared projects I am currently a member of."""
                return _db_get_projects(self.user)

            self.tools = [get_my_tickets, get_my_projects]

            # Model Strategy
            self.primary_model_name = 'gemini-flash-latest'
            self.backup_model_name = 'gemini-1.5-flash'
            
            # Start with primary
            self._init_chat(self.primary_model_name)
            
            # Send welcome message
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': f"Hello {self.user.first_name or self.user.username}! I'm your ConnectFlow Assistant. How can I help you today?"
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': "I'm sorry, but the AI Assistant is currently unavailable (API key missing). Please create a support ticket instead."
            }))

    def _init_chat(self, model_name, history=[]):
        """Initialize chat session with a specific model and history."""
        self.model = genai.GenerativeModel(
            model_name,
            tools=self.tools
        )
        self.chat = self.model.start_chat(
            history=history,
            enable_automatic_function_calling=True
        )
        self.current_model_name = model_name

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get('message')

        if not user_message:
            return

        if not hasattr(self, 'chat'):
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': "AI Assistant is not properly configured."
            }))
            return

        try:
            # System prompt to give context
            user_info = await self.get_user_context()

            system_context = (
                "You are the ConnectFlow Pro Support Assistant. "
                "ConnectFlow Pro is an organizational communication platform with real-time messaging, "
                "role-based access control, file uploads (Cloudinary), and project management features. "
                "Help the user with their questions about using the platform. "
                "Be professional, concise, and helpful. "
                "You have access to tools to look up the user's tickets and projects. "
                "ALWAYS check these tools if the user asks about their specific data. "
                "If you cannot help, suggest they create a support ticket.\n\n"
                f"Context about the user you are chatting with:\n{user_info}"
            )
            
            # Use fallback-aware response getter
            response = await self.get_ai_response(f"{system_context}\n\nUser says: {user_message}")
            
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': response
            }))
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                friendly_msg = "I'm currently overwhelmed with requests (Daily/Minute Quota Exceeded). Please try again in a few minutes."
            else:
                friendly_msg = f"I encountered an error while processing your request: {error_msg}"

            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': friendly_msg
            }))

    @database_sync_to_async
    def get_user_context(self):
        """Fetch user details safely in a sync context."""
        user_info = f"User: {self.user.get_full_name()} ({self.user.username})"
        # Accessing foreign keys triggers DB queries, so this must be sync
        if self.user.organization:
            user_info += f"\nOrganization: {self.user.organization.name}"
        user_info += f"\nRole: {self.user.get_role_display()}"
        return user_info

    async def get_ai_response(self, prompt):
        # Run the sync logic (with retry) in a thread
        return await database_sync_to_async(self._send_message_with_retry)(prompt)

    def _send_message_with_retry(self, prompt):
        """Try sending message with current model, switch to backup on 429."""
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            # Check for quota error (429 or ResourceExhausted)
            error_str = str(e)
            if ("429" in error_str or "ResourceExhausted" in error_str) and self.current_model_name == self.primary_model_name:
                # Switch to backup
                # Preserve history
                current_history = self.chat.history
                
                # Re-init with backup model
                self._init_chat(self.backup_model_name, history=current_history)
                
                # Retry send
                response = self.chat.send_message(prompt)
                return response.text
            else:
                # Re-raise if it's not a quota error OR we are already on backup
                raise e
