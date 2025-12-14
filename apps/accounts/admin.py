from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with additional fields."""
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar', 'bio')}),
        (_('Organization'), {'fields': ('organization', 'role')}),
        (_('Status'), {'fields': ('status', 'timezone')}),
        (_('Notifications'), {'fields': ('email_notifications', 'mention_notifications')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_seen')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'organization'),
        }),
    )
    
    list_display = ('username', 'email', 'get_full_name', 'role', 'organization', 'status', 'is_staff')
    list_filter = ('role', 'status', 'is_staff', 'is_superuser', 'is_active', 'organization')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'date_joined', 'last_seen')
    
    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'Full Name'
