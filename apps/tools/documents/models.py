from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
import os

class Folder(models.Model):
    """Hierarchical folder structure for documents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='document_folders'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subfolders'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Permissions
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_folders'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_folders'
        verbose_name = _('Folder')
        verbose_name_plural = _('Folders')
        ordering = ['name']
        unique_together = ['organization', 'parent', 'name']

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        if self.parent:
            return f"{self.parent.full_path} / {self.name}"
        return self.name


class Document(models.Model):
    """Main document metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Access Control
    is_public = models.BooleanField(
        default=False,
        help_text=_("Available to everyone in the organization")
    )
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Current version reference
    current_version = models.OneToOneField(
        'DocumentVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_doc'
    )

    class Meta:
        db_table = 'documents'
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def latest_version(self):
        return self.versions.order_by('-version_number').first()


def document_upload_path(instance, filename):
    # Upload to organization-specific folder
    return f"documents/org_{instance.document.organization.id}/{instance.document.id}/{filename}"

class DocumentVersion(models.Model):
    """Individual version of a document"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.IntegerField(default=1)
    
    file = models.FileField(upload_to=document_upload_path)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=100)
    
    change_log = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_versions'
        verbose_name = _('Document Version')
        verbose_name_plural = _('Document Versions')
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.document.title} (v{self.version_number})"

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = os.path.basename(self.file.name)
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
