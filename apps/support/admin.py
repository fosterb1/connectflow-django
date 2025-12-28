from django.contrib import admin
from .models import Ticket, TicketMessage

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'requester', 'status', 'priority', 'is_priority_support', 'created_at')
    list_filter = ('status', 'priority', 'is_priority_support', 'category')
    search_fields = ('subject', 'requester__username', 'requester__email', 'id')
    inlines = [TicketMessageInline]
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['mark_resolved', 'mark_closed']
    
    def mark_resolved(self, request, queryset):
        queryset.update(status=Ticket.Status.RESOLVED)
    mark_resolved.short_description = "Mark selected tickets as Resolved"

    def mark_closed(self, request, queryset):
        queryset.update(status=Ticket.Status.CLOSED)
    mark_closed.short_description = "Mark selected tickets as Closed"
