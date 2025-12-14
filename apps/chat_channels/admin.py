from django.contrib import admin
from .models import Channel, Message, MessageReaction, MessageReadReceipt


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin interface for Channel model."""
    
    list_display = ('name', 'channel_type', 'organization', 'department', 'team', 'member_count', 'is_private', 'is_archived', 'created_at')
    list_filter = ('channel_type', 'is_private', 'is_archived', 'read_only', 'organization', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    readonly_fields = ('id', 'member_count', 'created_at', 'updated_at')
    filter_horizontal = ('members',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'channel_type', 'organization')
        }),
        ('Related Entities', {
            'fields': ('department', 'team'),
            'description': 'Link to department or team (optional, depends on channel type)'
        }),
        ('Membership', {
            'fields': ('created_by', 'members')
        }),
        ('Settings', {
            'fields': ('is_private', 'is_archived', 'read_only')
        }),
        ('Metadata', {
            'fields': ('id', 'member_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Members'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    
    list_display = ('get_preview', 'sender', 'channel', 'reply_count', 'is_edited', 'created_at')
    list_filter = ('is_edited', 'is_deleted', 'channel', 'created_at')
    search_fields = ('content', 'sender__username', 'channel__name')
    readonly_fields = ('id', 'reply_count', 'reaction_summary', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Message Content', {
            'fields': ('channel', 'sender', 'content', 'file')
        }),
        ('Threading', {
            'fields': ('parent_message',)
        }),
        ('Status', {
            'fields': ('is_edited', 'is_deleted')
        }),
        ('Metadata', {
            'fields': ('id', 'reply_count', 'reaction_summary', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_preview(self, obj):
        return f"{obj.content[:50]}..." if len(obj.content) > 50 else obj.content
    get_preview.short_description = 'Preview'
    
    def reply_count(self, obj):
        return obj.reply_count
    reply_count.short_description = 'Replies'
    
    def reaction_summary(self, obj):
        return obj.reaction_summary or 'No reactions'
    reaction_summary.short_description = 'Reactions'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    """Admin interface for MessageReaction model."""
    
    list_display = ('emoji', 'user', 'message_preview', 'created_at')
    list_filter = ('emoji', 'created_at')
    search_fields = ('user__username', 'message__content')
    readonly_fields = ('id', 'created_at')
    
    def message_preview(self, obj):
        return f"{obj.message.content[:30]}..." if len(obj.message.content) > 30 else obj.message.content
    message_preview.short_description = 'Message'


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    """Admin interface for MessageReadReceipt model."""
    
    list_display = ('user', 'message_preview', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__username', 'message__content')
    readonly_fields = ('id', 'read_at')
    
    def message_preview(self, obj):
        return f"{obj.message.content[:30]}..." if len(obj.message.content) > 30 else obj.message.content
    message_preview.short_description = 'Message'
