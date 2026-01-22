from django.contrib import admin
from .models import Resource, Booking

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'resource_type', 'location', 'capacity', 'is_active']
    list_filter = ['resource_type', 'is_active', 'organization']
    search_fields = ['name', 'location', 'organization__name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource', 'user', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'resource__resource_type', 'start_time']
    search_fields = ['title', 'resource__name', 'user__username']
    date_hierarchy = 'start_time'
