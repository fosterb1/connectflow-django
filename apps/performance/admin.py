from django.contrib import admin
from .models import (
    KPIMetric, KPIThreshold, KPIAssignment,
    PerformanceReview, PerformanceScore, PerformanceAuditLog
)


@admin.register(KPIMetric)
class KPIMetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'metric_type', 'weight', 'role', 'is_active', 'version', 'created_at']
    list_filter = ['organization', 'metric_type', 'is_active', 'role']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'description', 'metric_type')
        }),
        ('Configuration', {
            'fields': ('weight', 'role', 'team')
        }),
        ('Status', {
            'fields': ('is_active', 'version', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(KPIThreshold)
class KPIThresholdAdmin(admin.ModelAdmin):
    list_display = ['metric', 'min_value', 'target_value', 'max_value', 'pass_fail_enabled']
    list_filter = ['pass_fail_enabled']
    search_fields = ['metric__name']


@admin.register(KPIAssignment)
class KPIAssignmentAdmin(admin.ModelAdmin):
    list_display = ['metric', 'user', 'review_period', 'assigned_by', 'assigned_at']
    list_filter = ['review_period', 'assigned_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'metric__name']
    readonly_fields = ['assigned_at']


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'reviewer', 'organization', 'review_period_start', 'review_period_end', 'final_score', 'status', 'finalized_at']
    list_filter = ['status', 'organization', 'review_period_end']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'reviewer__username']
    readonly_fields = ['created_at', 'finalized_at']
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'reviewer', 'organization')
        }),
        ('Review Period', {
            'fields': ('review_period_start', 'review_period_end')
        }),
        ('Results', {
            'fields': ('final_score', 'status', 'comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'finalized_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PerformanceScore)
class PerformanceScoreAdmin(admin.ModelAdmin):
    list_display = ['review', 'metric', 'calculated_score', 'manual_override_score', 'overridden_by', 'updated_at']
    list_filter = ['review__status', 'metric__metric_type']
    search_fields = ['review__user__username', 'metric__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PerformanceAuditLog)
class PerformanceAuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'actor', 'target_user', 'organization', 'timestamp']
    list_filter = ['action', 'organization', 'timestamp']
    search_fields = ['actor__username', 'target_user__username', 'reason']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

