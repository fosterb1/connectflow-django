from django import forms
from django.contrib.auth import get_user_model
from .models import Channel, Message
from apps.organizations.models import Department, Team

User = get_user_model()


class ChannelForm(forms.ModelForm):
    """Form for creating and editing channels."""
    
    class Meta:
        model = Channel
        fields = ['name', 'description', 'channel_type', 'department', 'team', 'members', 'is_private', 'read_only']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., general, announcements, project-alpha'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Channel description...',
                'rows': 3
            }),
            'channel_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'team': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'members': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'size': '5'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            }),
            'read_only': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            })
        }
    
    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if organization:
            # Filter departments and teams by organization
            self.fields['department'].queryset = Department.objects.filter(organization=organization)
            self.fields['team'].queryset = Team.objects.filter(department__organization=organization)
            self.fields['members'].queryset = User.objects.filter(organization=organization)
        else:
            self.fields['department'].queryset = Department.objects.none()
            self.fields['team'].queryset = Team.objects.none()
            self.fields['members'].queryset = User.objects.none()
        
        # Make fields optional
        self.fields['department'].required = False
        self.fields['team'].required = False
        self.fields['members'].required = False


class MessageForm(forms.ModelForm):
    """Form for sending messages in channels."""
    
    class Meta:
        model = Message
        fields = ['content', 'file', 'voice_message', 'voice_duration', 'parent_message']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none',
                'placeholder': 'Type your message... (Shift+Enter for new line)',
                'rows': 3
            }),
            'file': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'file-upload'
            }),
            'voice_message': forms.HiddenInput(attrs={'id': 'voice-message-input'}),
            'voice_duration': forms.HiddenInput(attrs={'id': 'voice-duration-input'}),
            'parent_message': forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        self.fields['file'].required = False
        self.fields['voice_message'].required = False
        self.fields['voice_duration'].required = False
        self.fields['parent_message'].required = False
