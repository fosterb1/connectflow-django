from rest_framework import serializers
from .models import Ticket, TicketMessage
from apps.accounts.serializers import UserSerializer

class TicketMessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_details', 'content', 'attachment', 'is_internal_note', 'created_at']
        read_only_fields = ['sender', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    requester_details = UserSerializer(source='requester', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'requester', 'requester_details', 'organization', 'subject', 
            'category', 'status', 'priority', 'is_priority_support', 
            'assigned_to', 'assigned_to_details', 'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['requester', 'is_priority_support', 'created_at', 'updated_at']
