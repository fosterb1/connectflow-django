import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"notifications_{self.user.id}"
        
        # Join personal notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'id': event['id'],
            'title': event['title'],
            'content': event['content'],
            'notification_type': event['notification_type'],
            'link': event['link'],
            'created_at': event['created_at']
        }))


class PresenceConsumer(AsyncWebsocketConsumer):
    """
    Global presence tracking - maintains user online status across all pages.
    """
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join organization-wide presence group
        if self.user.organization_id:
            self.org_group = f'presence_org_{self.user.organization_id}'
            await self.channel_layer.group_add(self.org_group, self.channel_name)
        
        # Set user ONLINE
        await self.set_status('ONLINE')
        
        # Broadcast to organization
        if hasattr(self, 'org_group'):
            await self.channel_layer.group_send(
                self.org_group,
                {
                    'type': 'user_status_update',
                    'user_id': self.user.id,
                    'status': 'ONLINE'
                }
            )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'org_group'):
            # Set user OFFLINE
            await self.set_status('OFFLINE')
            
            # Broadcast to organization
            await self.channel_layer.group_send(
                self.org_group,
                {
                    'type': 'user_status_update',
                    'user_id': self.user.id,
                    'status': 'OFFLINE'
                }
            )
            
            await self.channel_layer.group_discard(self.org_group, self.channel_name)
    
    async def receive(self, text_data):
        """Handle heartbeat pings and status changes."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        
        if data.get('type') == 'heartbeat':
            # Update last_seen on heartbeat
            await self.update_activity()
            await self.send(text_data=json.dumps({'type': 'pong'}))
        
        elif data.get('type') == 'status_change':
            # Manual status change (AWAY, BUSY, ONLINE)
            new_status = data.get('status', '').upper()
            if new_status in ['ONLINE', 'AWAY', 'BUSY']:
                await self.set_status(new_status)
                if hasattr(self, 'org_group'):
                    await self.channel_layer.group_send(
                        self.org_group,
                        {
                            'type': 'user_status_update',
                            'user_id': self.user.id,
                            'status': new_status
                        }
                    )
    
    async def user_status_update(self, event):
        """Broadcast status changes to all connected clients."""
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'user_id': event['user_id'],
            'status': event['status']
        }))
    
    @database_sync_to_async
    def set_status(self, status):
        User.objects.filter(id=self.user.id).update(
            status=status,
            last_seen=timezone.now()
        )
    
    @database_sync_to_async
    def update_activity(self):
        User.objects.filter(id=self.user.id).update(last_seen=timezone.now())
