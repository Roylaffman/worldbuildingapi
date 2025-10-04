"""
Admin interface for managing soft-deleted content.
Provides easy access to restore or permanently delete content.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Page, Character, Story, Essay, Image


class SoftDeletedContentAdmin(admin.ModelAdmin):
    """Base admin for viewing and managing soft-deleted content."""
    
    list_display = ['title', 'author', 'world', 'deleted_at', 'deleted_by', 'restore_link', 'purge_link']
    list_filter = ['deleted_at', 'deleted_by', 'world']
    search_fields = ['title', 'author__username', 'world__title']
    readonly_fields = ['title', 'content', 'author', 'world', 'created_at', 'deleted_at', 'deleted_by']
    
    def get_queryset(self, request):
        """Show only soft-deleted content."""
        return self.model.all_objects.filter(is_deleted=True)
    
    def restore_link(self, obj):
        """Link to restore this content."""
        url = reverse('admin:restore_content', args=[obj._meta.app_label, obj._meta.model_name, obj.pk])
        return format_html('<a href="{}" class="button">Restore</a>', url)
    restore_link.short_description = 'Restore'
    
    def purge_link(self, obj):
        """Link to permanently delete this content."""
        url = reverse('admin:purge_content', args=[obj._meta.app_label, obj._meta.model_name, obj.pk])
        return format_html('<a href="{}" class="button" style="background-color: #dc3545;">Purge</a>', url)
    purge_link.short_description = 'Permanent Delete'
    
    def has_add_permission(self, request):
        """Don't allow adding deleted content through admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing but not editing."""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow regular delete (use purge instead)."""
        return False


# Register soft-deleted content admin views
@admin.register(Page)
class DeletedPageAdmin(SoftDeletedContentAdmin):
    pass


@admin.register(Character)
class DeletedCharacterAdmin(SoftDeletedContentAdmin):
    list_display = SoftDeletedContentAdmin.list_display + ['species', 'occupation']


@admin.register(Story)
class DeletedStoryAdmin(SoftDeletedContentAdmin):
    list_display = SoftDeletedContentAdmin.list_display + ['genre', 'story_type']


@admin.register(Essay)
class DeletedEssayAdmin(SoftDeletedContentAdmin):
    list_display = SoftDeletedContentAdmin.list_display + ['topic']


@admin.register(Image)
class DeletedImageAdmin(SoftDeletedContentAdmin):
    list_display = SoftDeletedContentAdmin.list_display + ['image_url']