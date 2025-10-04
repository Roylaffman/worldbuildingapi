"""
Management command to manage soft-deleted content.
Allows viewing, restoring, or permanently deleting soft-deleted content.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from collab.models import World, Page, Character, Story, Essay, Image
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Manage soft-deleted content (view, restore, or permanently delete)'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'restore', 'purge'],
            help='Action to perform: list (show deleted), restore (undelete), or purge (permanently delete)'
        )
        parser.add_argument(
            '--content-type',
            choices=['page', 'character', 'story', 'essay', 'image', 'world'],
            help='Filter by content type'
        )
        parser.add_argument(
            '--id',
            type=int,
            help='Specific content ID to restore or purge'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='For purge: permanently delete content soft-deleted more than X days ago (default: 30)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Required for restore and purge operations'
        )

    def handle(self, *args, **options):
        action = options['action']
        content_type = options['content_type']
        content_id = options['id']
        days = options['days']
        force = options['force']

        if action in ['restore', 'purge'] and not force:
            self.stdout.write(
                self.style.ERROR(
                    f'{action.capitalize()} operations require --force flag'
                )
            )
            return

        # Define content models
        content_models = {
            'page': Page,
            'character': Character,
            'story': Story,
            'essay': Essay,
            'image': Image,
            'world': World
        }

        if action == 'list':
            self._list_deleted_content(content_models, content_type)
        elif action == 'restore':
            self._restore_content(content_models, content_type, content_id)
        elif action == 'purge':
            self._purge_content(content_models, content_type, content_id, days)

    def _list_deleted_content(self, content_models, content_type_filter):
        """List all soft-deleted content."""
        self.stdout.write(self.style.SUCCESS('Soft-Deleted Content:'))
        self.stdout.write('=' * 50)

        total_deleted = 0

        for content_type, model_class in content_models.items():
            if content_type_filter and content_type != content_type_filter:
                continue

            if hasattr(model_class, 'all_objects'):
                deleted_items = model_class.all_objects.filter(is_deleted=True)
            else:
                continue  # Skip models without soft delete

            count = deleted_items.count()
            total_deleted += count

            if count > 0:
                self.stdout.write(f'\n{content_type.capitalize()}s ({count}):')
                for item in deleted_items[:10]:  # Show first 10
                    deleted_info = f"  ID: {item.id} | {item.title[:50]}"
                    if hasattr(item, 'deleted_at') and item.deleted_at:
                        deleted_info += f" | Deleted: {item.deleted_at.strftime('%Y-%m-%d %H:%M')}"
                    if hasattr(item, 'deleted_by') and item.deleted_by:
                        deleted_info += f" | By: {item.deleted_by.username}"
                    self.stdout.write(deleted_info)
                
                if count > 10:
                    self.stdout.write(f"  ... and {count - 10} more")

        self.stdout.write(f'\nTotal soft-deleted items: {total_deleted}')

    def _restore_content(self, content_models, content_type_filter, content_id):
        """Restore soft-deleted content."""
        if content_id:
            # Restore specific item
            if not content_type_filter:
                self.stdout.write(
                    self.style.ERROR('--content-type required when using --id')
                )
                return

            model_class = content_models.get(content_type_filter)
            if not model_class or not hasattr(model_class, 'all_objects'):
                self.stdout.write(
                    self.style.ERROR(f'Invalid content type: {content_type_filter}')
                )
                return

            try:
                item = model_class.all_objects.get(id=content_id, is_deleted=True)
                item.restore()
                self.stdout.write(
                    self.style.SUCCESS(f'Restored {content_type_filter} "{item.title}" (ID: {content_id})')
                )
            except model_class.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'No deleted {content_type_filter} found with ID {content_id}')
                )
        else:
            # Restore all deleted content of specified type
            restored_count = 0
            
            for content_type, model_class in content_models.items():
                if content_type_filter and content_type != content_type_filter:
                    continue

                if hasattr(model_class, 'all_objects'):
                    deleted_items = model_class.all_objects.filter(is_deleted=True)
                    for item in deleted_items:
                        item.restore()
                        restored_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Restored {restored_count} items')
            )

    def _purge_content(self, content_models, content_type_filter, content_id, days):
        """Permanently delete soft-deleted content."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        if content_id:
            # Purge specific item
            if not content_type_filter:
                self.stdout.write(
                    self.style.ERROR('--content-type required when using --id')
                )
                return

            model_class = content_models.get(content_type_filter)
            if not model_class or not hasattr(model_class, 'all_objects'):
                self.stdout.write(
                    self.style.ERROR(f'Invalid content type: {content_type_filter}')
                )
                return

            try:
                item = model_class.all_objects.get(id=content_id, is_deleted=True)
                title = item.title
                # Force permanent deletion
                super(model_class, item).delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Permanently deleted {content_type_filter} "{title}" (ID: {content_id})')
                )
            except model_class.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'No deleted {content_type_filter} found with ID {content_id}')
                )
        else:
            # Purge old deleted content
            purged_count = 0
            
            for content_type, model_class in content_models.items():
                if content_type_filter and content_type != content_type_filter:
                    continue

                if hasattr(model_class, 'all_objects'):
                    old_deleted = model_class.all_objects.filter(
                        is_deleted=True,
                        deleted_at__lt=cutoff_date
                    )
                    
                    count = old_deleted.count()
                    if count > 0:
                        self.stdout.write(f'Purging {count} old {content_type}s...')
                        for item in old_deleted:
                            super(model_class, item).delete()
                            purged_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Permanently deleted {purged_count} items older than {days} days')
            )