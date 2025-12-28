from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
from cloudinary.models import CloudinaryField

class Ticket(models.Model):
    """
    Represents a support request from a user.
    """
    class Category(models.TextChoices):
        BILLING = 'BILLING', _('Billing & Subscription')
        TECHNICAL = 'TECHNICAL', _('Technical Issue')
        ACCOUNT = 'ACCOUNT', _('Account & Access')
        FEATURE = 'FEATURE', _('Feature Request')
        OTHER = 'OTHER', _('Other')

    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        AWAITING_USER = 'AWAITING_USER', _('Awaiting User Reply')
        RESOLVED = 'RESOLVED', _('Resolved')
        CLOSED = 'CLOSED', _('Closed')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        help_text=_("User who opened the ticket")
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='tickets',
        null=True, # In case user has no org or system issue
        blank=True
    )
    
    subject = models.CharField(max_length=255)
    
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.TECHNICAL
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    is_priority_support = models.BooleanField(
        default=False,
        help_text=_("Flagged for priority support based on plan")
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets',
        null=True,
        blank=True,
        help_text=_("Staff member assigned to this ticket")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-is_priority_support', '-created_at'] 
        verbose_name = _('Support Ticket')
        verbose_name_plural = _('Support Tickets')

    def save(self, *args, **kwargs):
        # Auto-detect priority support entitlement on creation
        if not self.pk and self.requester.organization:
            self.organization = self.requester.organization
            if self.organization.has_feature('has_priority_support'):
                self.is_priority_support = True
                # Bump priority if not manually set to something specific yet
                if self.priority == self.Priority.MEDIUM:
                    self.priority = self.Priority.HIGH
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.status}] {self.subject} ({self.id})"


class TicketMessage(models.Model):
    """
    Individual messages within a ticket thread.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    content = models.TextField()
    
    attachment = CloudinaryField(
        'attachment',
        folder='support/attachments',
        resource_type='auto',
        null=True,
        blank=True
    )
    
    is_internal_note = models.BooleanField(
        default=False,
        help_text=_("Visible only to staff")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'support_ticket_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message by {self.sender} on {self.created_at}"
