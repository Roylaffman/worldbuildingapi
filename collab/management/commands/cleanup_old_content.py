"""
Management command to clean up old, unused content while preserving immutability.
This provides a compromise between immutability and database growth.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from collab.models import World, Page, Character, Story, Essay, Image
from django.db.models import Count, Q


class Command(BaseCommand):
    help = 'Clean up old, unused content to manage database growth'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete content older than this many days (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Actually perform the deletion (required for real cleanup)'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        force = options['force']
        
        if not dry_run and not force:
            self.stdout.write(
                self.style.ERROR(
                    'This command requires either --dry-run or --force flag'
                )
            )
            return

        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Looking for content older than {days} days ({cutoff_date})')
        
        # Define content models
        content_models = [
            ('Pages', Page),
            ('Characters', Character), 
            ('Stories', Story),
            ('Essays', Essay),
            ('Images', Image)
        ]
        
        total_deleted = 0
        
        for model_name, model_class in content_models:
            # Find old content with no links (not referenced by other content)
            old_content = model_class.objects.filter(
                created_at__lt=cutoff_date
            ).annotate(
                link_count=Count('linked_from_content')
            ).filter(
                link_count=0  # No other content links to this
            )
            
            count = old_content.count()
            
            if count > 0:
                self.stdout.write(f'Found {count} old {model_name.lower()} to clean up')
                
                if not dry_run:
                    # Temporarily bypass immutability for cleanup
                    for item in old_content:
                        try:
                            # Force delete by bypassing the immutable mixin
                            super(model_class, item).delete()
                            total_deleted += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error deleting {item}: {e}')
                            )
                else:
                    self.stdout.write(f'Would delete {count} {model_name.lower()}')
        
        # Clean up empty worlds (worlds with no content)
        empty_worlds = World.objects.annotate(
            content_count=Count('pages') + Count('characters') + Count('stories') + Count('essays') + Count('images')
        ).filter(
            content_count=0,
            created_at__lt=cutoff_date
        )
        
        empty_count = empty_worlds.count()
        if empty_count > 0:
            self.stdout.write(f'Found {empty_count} empty worlds to clean up')
            
            if not dry_run:
                deleted_worlds = empty_worlds.delete()[0]
                total_deleted += deleted_worlds
            else:
                self.stdout.write(f'Would delete {empty_count} empty worlds')
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dry run complete. Would clean up {total_deleted} items total.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Cleanup complete. Deleted {total_deleted} items total.'
                )
            )
            
        self.stdout.write('\nRecommendations:')
        self.stdout.write('- Run this monthly with --days=90 to clean up old unused content')
        self.stdout.write('- Use --dry-run first to see what would be deleted')
        self.stdout.write('- Content with links to other content is preserved')
        self.stdout.write('- Only truly orphaned content is removed')