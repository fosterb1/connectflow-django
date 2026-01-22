from django.contrib import admin
from .models import Folder, Document, DocumentVersion

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'parent', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['name', 'organization__name']

class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ['file_size', 'file_type', 'created_at']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'folder', 'is_public', 'updated_at']
    list_filter = ['organization', 'is_public', 'updated_at']
    search_fields = ['title', 'description', 'organization__name']
    inlines = [DocumentVersionInline]

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'file_name', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['file_name', 'document__title']
