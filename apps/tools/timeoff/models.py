from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid

class LeaveType(models.Model):
    """Categories of time off"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='leave_types'
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    # Policy
    requires_approval = models.BooleanField(default=True)
    counts_as_leave = models.BooleanField(
        default=True,
        help_text=_("Whether this deducts from leave balance")
    )
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text=_("Hex color code for calendar display")
    )

    class Meta:
        db_table = 'leave_types'
        unique_together = ['organization', 'name']
        verbose_name = _('Leave Type')
        verbose_name_plural = _('Leave Types')

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    """Individual leave request"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        CANCELLED = 'CANCELLED', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name='requests'
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=4, decimal_places=1)
    
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Approval
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests'
    )
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_requests'
        verbose_name = _('Leave Request')
        verbose_name_plural = _('Leave Requests')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} ({self.start_date})"


class LeaveBalance(models.Model):
    """User's accrued leave balance for a year"""
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='user_balances'
    )
    year = models.IntegerField()
    
    total_allocated = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )
    used = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )
    
    class Meta:
        db_table = 'leave_balances'
        unique_together = ['user', 'leave_type', 'year']
        verbose_name = _('Leave Balance')
        verbose_name_plural = _('Leave Balances')

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} ({self.year})"

    @property
    def remaining(self):
        return self.total_allocated - self.used

    @property
    def percent_used(self):
        if self.total_allocated > 0:
            return (self.used / self.total_allocated) * 100
        return 0
