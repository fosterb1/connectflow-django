from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid

class Resource(models.Model):
    """Shared organizational resource (room, equipment, etc.)"""
    
    class ResourceType(models.TextChoices):
        MEETING_ROOM = 'MEETING_ROOM', _('Meeting Room')
        EQUIPMENT = 'EQUIPMENT', _('Equipment')
        VEHICLE = 'VEHICLE', _('Vehicle')
        HOT_DESK = 'HOT_DESK', _('Hot Desk')
        OTHER = 'OTHER', _('Other')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='resources'
    )
    
    name = models.CharField(max_length=100)
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.MEETING_ROOM
    )
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    capacity = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    
    # Availability
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resources'
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"


class Booking(models.Model):
    """A reservation for a resource"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Approval')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        COMPLETED = 'COMPLETED', _('Completed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='resource_bookings'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED
    )
    
    # Approval
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_bookings'
    )
    approval_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} - {self.resource.name}"
