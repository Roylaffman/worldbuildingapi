"""
Management command for hard deletion of content and worlds.
Bypasses immutability for testing and administrative purposes.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from collab.models import World, Page, Character, Story, Essay, Image
from django.db import transaction


class Command(BaseCommand):
    help = 'Hard delete content and worlds (bypasses immutability)'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'delete-world', 'delete-content', 'delete-user-data', 'reset-test-data'],
            help='Action to perform'
        )
        parser.add_argument(
            '--world-id',
            type=int,
            help='Specific world ID to delete'
        )
        parser.add_argument(
            '--content-type',
            choices=['page', 'character', 'story', 'essay', 'image'],
            help='Content type to delete'
        )
        parser.add_argument(
            '--content-id',
            type=int,
            help='Specific content ID to delete'
        )
        parser.add_argument(
            '--user',
            help='Username to delete all data for'
        )
        parser.add_argument(
            '--pattern',
            help='Delete worlds/content matching this title pattern (case-insensitive)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Required for all delete operations'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        action = options['action']
        force = options['force']
        dry_run = options['dry_run']

        if action != 'list' and not force and not dry_run:
            self.stdout.write(
                self.style.ERROR(
                    'Delete operations require either --force or --dry-run flag'
                )
            )
            return

        if action == 'list':
            self._list_content()
        elif action == 'delete-world':
            self._delete_world(options, dry_run)
        elif action == 'delete-content':
            self._delete_content(options, dry_run)
        elif action == 'delete-user-data':
            self._delete_user_data(options, dry_run)
        elif action == 'reset-test-data':
            self._reset_test_data(dry_run)

    def _list_content(self):
        """List all content in the database."""
        self.stdout.write(self.style.SUCCESS('Database Content Summary:'))
        self.stdout.write('=' * 50)

        # List worlds
        worlds = World.objects.all().order_by('-created_at')
        self.stdout.write(f'\nWorlds ({worlds.count()}):')
        for world in worlds[:10]:
            content_count = (
                world.page_entries.count() + 
                world.character_entries.count() + 
                world.story_entries.count() + 
                world.essay_entries.count() + 
                world.image_entries.count()
            )
            self.stdout.write(
                f'  ID: {world.id} | "{world.title}" | Creator: {world.creator.username} | Content: {content_count} | Created: {world.created_at.strftime("%Y-%m-%d")}'
            )
        
        if worlds.count() > 10:
            self.stdout.write(f'  ... and {worlds.count() - 10} more worlds')

        # List content by type
        content_models = {
            'Pages': Page,
            'Characters': Character,
            'Stories': Story,
            'Essays': Essay,
            'Images': Image
        }

        for name, model in content_models.items():
            if hasattr(model, 'all_objects'):
                total = model.all_objects.count()
                active = model.objects.count()
                deleted = total - active
            else:
                total = active = model.objects.count()
                deleted = 0
            
            self.stdout.write(f'\n{name}: {total} total ({active} active, {deleted} soft-deleted)')

    def _delete_world(self, options, dry_run):
        """Delete specific world(s)."""
        world_id = options.get('world_id')
        pattern = options.get('pattern')

        if world_id:
            try:
                world = World.objects.get(id=world_id)
                self._delete_world_and_content(world, dry_run)
            except World.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'World with ID {world_id} not found')
                )
        elif pattern:
            worlds = World.objects.filter(title__icontains=pattern)
            if not worlds.exists():
                self.stdout.write(
                    self.style.ERROR(f'No worlds found matching pattern: {pattern}')
                )
                return
            
            self.stdout.write(f'Found {worlds.count()} worlds matching "{pattern}":')
            for world in worlds:
                self.stdout.write(f'  - ID: {world.id} | "{world.title}"')
            
            if not dry_run:
                confirm = input(f'\nDelete all {worlds.count()} worlds? (yes/no): ')
                if confirm.lower() != 'yes':
                    self.stdout.write('Cancelled.')
                    return
            
            for world in worlds:
                self._delete_world_and_content(world, dry_run)
        else:
            self.stdout.write(
                self.style.ERROR('Either --world-id or --pattern is required')
            )

    def _delete_world_and_content(self, world, dry_run):
        """Delete a world and all its content."""
        content_count = (
            world.page_entries.count() + 
            world.character_entries.count() + 
            world.story_entries.count() + 
            world.essay_entries.count() + 
            world.image_entries.count()
        )

        if dry_run:
            self.stdout.write(
                f'Would delete world "{world.title}" (ID: {world.id}) and {content_count} content items'
            )
        else:
            with transaction.atomic():
                # Delete all content in the world (bypassing immutability)
                for model_class in [Page, Character, Story, Essay, Image]:
                    if hasattr(model_class, 'all_objects'):
                        content_items = model_class.all_objects.filter(world=world)
                    else:
                        content_items = model_class.objects.filter(world=world)
                    
                    for item in content_items:
                        super(model_class, item).delete()
                
                # Delete the world itself
                world.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Deleted world "{world.title}" and {content_count} content items'
                    )
                )

    def _delete_content(self, options, dry_run):
        """Delete specific content."""
        content_type = options.get('content_type')
        content_id = options.get('content_id')
        pattern = options.get('pattern')

        if not content_type:
            self.stdout.write(
                self.style.ERROR('--content-type is required')
            )
            return

        model_map = {
            'page': Page,
            'character': Character,
            'story': Story,
            'essay': Essay,
            'image': Image
        }

        model_class = model_map[content_type]
        manager = model_class.all_objects if hasattr(model_class, 'all_objects') else model_class.objects

        if content_id:
            try:
                item = manager.get(id=content_id)
                if dry_run:
                    self.stdout.write(f'Would delete {content_type} "{item.title}" (ID: {content_id})')
                else:
                    title = item.title
                    super(model_class, item).delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'Deleted {content_type} "{title}"')
                    )
            except model_class.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'{content_type.capitalize()} with ID {content_id} not found')
                )
        elif pattern:
            items = manager.filter(title__icontains=pattern)
            count = items.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.ERROR(f'No {content_type}s found matching pattern: {pattern}')
                )
                return
            
            if dry_run:
                self.stdout.write(f'Would delete {count} {content_type}s matching "{pattern}"')
            else:
                for item in items:
                    super(model_class, item).delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {count} {content_type}s')
                )

    def _delete_user_data(self, options, dry_run):
        """Delete all data for a specific user."""
        username = options.get('user')
        if not username:
            self.stdout.write(
                self.style.ERROR('--user is required')
            )
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found')
            )
            return

        # Count user's data
        worlds = World.objects.filter(creator=user)
        content_counts = {}
        total_content = 0

        for model_name, model_class in [('pages', Page), ('characters', Character), 
                                       ('stories', Story), ('essays', Essay), ('images', Image)]:
            if hasattr(model_class, 'all_objects'):
                count = model_class.all_objects.filter(author=user).count()
            else:
                count = model_class.objects.filter(author=user).count()
            content_counts[model_name] = count
            total_content += count

        if dry_run:
            self.stdout.write(f'Would delete all data for user "{username}":')
            self.stdout.write(f'  - {worlds.count()} worlds')
            for content_type, count in content_counts.items():
                self.stdout.write(f'  - {count} {content_type}')
            self.stdout.write(f'  Total: {total_content} content items')
        else:
            with transaction.atomic():
                # Delete user's content
                for model_class in [Page, Character, Story, Essay, Image]:
                    if hasattr(model_class, 'all_objects'):
                        user_content = model_class.all_objects.filter(author=user)
                    else:
                        user_content = model_class.objects.filter(author=user)
                    
                    for item in user_content:
                        super(model_class, item).delete()
                
                # Delete user's worlds
                for world in worlds:
                    world.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Deleted all data for user "{username}": {worlds.count()} worlds, {total_content} content items'
                    )
                )

    def _reset_test_data(self, dry_run):
        """Reset all test data (worlds with 'test' in the name)."""
        test_patterns = ['test', 'static', 'demo', 'example']
        test_worlds = World.objects.none()
        
        for pattern in test_patterns:
            test_worlds = test_worlds | World.objects.filter(title__icontains=pattern)
        
        test_worlds = test_worlds.distinct()
        
        if test_worlds.count() == 0:
            self.stdout.write('No test worlds found.')
            return
        
        total_content = 0
        for world in test_worlds:
            total_content += (
                world.page_entries.count() + 
                world.character_entries.count() + 
                world.story_entries.count() + 
                world.essay_entries.count() + 
                world.image_entries.count()
            )
        
        if dry_run:
            self.stdout.write(f'Would delete {test_worlds.count()} test worlds and {total_content} content items:')
            for world in test_worlds:
                self.stdout.write(f'  - "{world.title}" (ID: {world.id})')
        else:
            confirm = input(f'Delete {test_worlds.count()} test worlds and {total_content} content items? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Cancelled.')
                return
            
            for world in test_worlds:
                self._delete_world_and_content(world, False)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Reset complete: deleted {test_worlds.count()} test worlds and {total_content} content items'
                )
            )