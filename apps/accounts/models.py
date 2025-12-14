from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for ConnectFlow Pro.
    Extends Django's AbstractUser to add role-based access and profile fields.
    """
    
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')
        DEPT_HEAD = 'DEPT_HEAD', _('Department Head')
        TEAM_MANAGER = 'TEAM_MANAGER', _('Team Manager')
        TEAM_MEMBER = 'TEAM_MEMBER', _('Team Member')
    
    class Status(models.TextChoices):
        ONLINE = 'ONLINE', _('Online')
        OFFLINE = 'OFFLINE', _('Offline')
        AWAY = 'AWAY', _('Away')
        BUSY = 'BUSY', _('Busy')
    
    # Role and organization
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TEAM_MEMBER,
        help_text=_("User's role in the organization")
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True,
        help_text=_("Organization this user belongs to")
    )
    
    # Profile fields
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text=_("User profile picture")
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text=_("Short bio or description")
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Contact phone number")
    )
    
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text=_("User's timezone")
    )
    
    # Status and presence
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OFFLINE,
        help_text=_("Current online status")
    )
    
    last_seen = models.DateTimeField(
        auto_now=True,
        help_text=_("Last activity timestamp")
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text=_("Receive email notifications")
    )
    
    mention_notifications = models.BooleanField(
        default=True,
        help_text=_("Get notified when mentioned")
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_admin(self):
        """Check if user is a Super Admin."""
        return self.role == self.Role.SUPER_ADMIN
    
    @property
    def is_manager(self):
        """Check if user is a Department Head or Team Manager."""
        return self.role in [self.Role.DEPT_HEAD, self.Role.TEAM_MANAGER]
