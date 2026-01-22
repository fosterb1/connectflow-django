from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class Announcement(models.Model):
    """Broadcast messages for the organization"""
    
    class Priority(models.TextChoices):
        NORMAL = 'NORMAL', _('Normal')
        IMPORTANT = 'IMPORTANT', _('Important')
        URGENT = 'URGENT', _('Urgent')
        CRITICAL = 'CRITICAL', _('Critical')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    
    # Targeting
    target_department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targeted_announcements'
    )
    target_team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targeted_announcements'
    )
    target_role = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Target specific user role")
    )
    
    # Scheduling & Status
    is_published = models.BooleanField(default=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Features
    require_acknowledgement = models.BooleanField(
        default=False,
        help_text=_("Users must click a button to acknowledge they read this")
    )
    is_pinned = models.BooleanField(default=False)
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='created_announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'announcements'
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        if not self.is_published:
            return False
        if self.scheduled_at and now < self.scheduled_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True


class AnnouncementReadReceipt(models.Model):
    """Tracks which users have read an announcement"""
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='read_receipts'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='announcement_receipts'
    )
    
    read_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'announcement_read_receipts'
        unique_together = ['announcement', 'user']
        verbose_name = _('Read Receipt')
        verbose_name_plural = _('Read Receipts')

    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"
