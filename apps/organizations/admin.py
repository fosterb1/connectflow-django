from django.contrib import admin
from .models import Organization, Department, Team


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organization model."""
    
    list_display = ('name', 'code', 'timezone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'logo', 'description')
        }),
        ('Settings', {
            'fields': ('timezone', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""
    
    list_display = ('name', 'organization', 'head', 'member_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'organization', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    readonly_fields = ('id', 'member_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'description')
        }),
        ('Management', {
            'fields': ('head', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'member_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Total Members'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""
    
    list_display = ('name', 'department', 'manager', 'member_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'department__organization', 'department', 'created_at')
    search_fields = ('name', 'description', 'department__name')
    readonly_fields = ('id', 'member_count', 'created_at', 'updated_at')
    filter_horizontal = ('members',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'name', 'description')
        }),
        ('Management', {
            'fields': ('manager', 'members', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'member_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Members'
