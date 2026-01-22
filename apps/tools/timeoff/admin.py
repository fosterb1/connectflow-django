from django.contrib import admin
from .models import LeaveType, LeaveRequest, LeaveBalance

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'requires_approval', 'counts_as_leave']
    list_filter = ['organization', 'requires_approval']
    search_fields = ['name']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'start_date', 'end_date', 'total_days', 'status']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['user__username', 'reason']
    date_hierarchy = 'start_date'

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'year', 'total_allocated', 'used', 'remaining']
    list_filter = ['year', 'leave_type']
    search_fields = ['user__username']
