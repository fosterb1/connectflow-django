from django.contrib import admin
from .models import Announcement, AnnouncementReadReceipt

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'priority', 'is_published', 'is_pinned', 'created_at']
    list_filter = ['priority', 'is_published', 'is_pinned', 'organization']
    search_fields = ['title', 'content', 'organization__name']
    date_hierarchy = 'created_at'

@admin.register(AnnouncementReadReceipt)
class AnnouncementReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'read_at', 'acknowledged_at']
    list_filter = ['read_at', 'acknowledged_at']
    search_fields = ['announcement__title', 'user__username']
