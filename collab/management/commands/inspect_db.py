"""
Comprehensive database inspection and management commands.
Provides detailed views into the database structure and content.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from collab.models import World, Page, Character, Story, Essay, Image, UserProfile, Tag, ContentLink
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json


class Command(BaseCommand):
    help = 'Inspect and analyze database content'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=[
                'overview', 'worlds', 'content', 'users', 'tags', 'links',
                'world-detail', 'user-detail', 'content-detail', 'stats',
                'search', 'recent', 'empty-worlds', 'orphaned-content'
            ],
            help='Type of inspection to perform'
        )
        parser.add_argument(
            '--id',
            type=int,
            help='Specific ID to inspect (for detail commands)'
        )
        parser.add_argument(
            '--user',
            help='Username to inspect'
        )
        parser.add_argument(
            '--world',
            type=int,
            help='World ID to filter by'
        )
        parser.add_argument(
            '--content-type',
            choices=['page', 'character', 'story', 'essay', 'image'],
            help='Content type to filter by'
        )
        parser.add_argument(
            '--search',
            help='Search term for titles/content'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Limit number of results (default: 20)'
        )
        parser.add_argument(
            '--include-deleted',
            action='store_true',
            help='Include soft-deleted content'
        )
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'detailed'],
            default='table',
            help='Output format'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'overview':
            self._show_overview(options)
        elif action == 'worlds':
            self._show_worlds(options)
        elif action == 'content':
            self._show_content(options)
        elif action == 'users':
            self._show_users(options)
        elif action == 'tags':
            self._show_tags(options)
        elif action == 'links':
            self._show_links(options)
        elif action == 'world-detail':
            self._show_world_detail(options)
        elif action == 'user-detail':
            self._show_user_detail(options)
        elif action == 'content-detail':
            self._show_content_detail(options)
        elif action == 'stats':
            self._show_stats(options)
        elif action == 'search':
            self._search_content(options)
        elif action == 'recent':
            self._show_recent(options)
        elif action == 'empty-worlds':
            self._show_empty_worlds(options)
        elif action == 'orphaned-content':
            self._show_orphaned_content(options)

    def _show_overview(self, options):
        """Show database overview."""
        self.stdout.write(self.style.SUCCESS('🗄️  Database Overview'))
        self.stdout.write('=' * 60)

        # Users
        total_users = User.objects.count()
        active_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        self.stdout.write(f'\n👥 Users: {total_users} total, {active_users} active (last 30 days)')

        # Worlds
        worlds = World.objects.all()
        public_worlds = worlds.filter(is_public=True).count()
        private_worlds = worlds.filter(is_public=False).count()
        
        self.stdout.write(f'\n🌍 Worlds: {worlds.count()} total ({public_worlds} public, {private_worlds} private)')

        # Content by type
        content_models = {
            'Pages': Page,
            'Characters': Character,
            'Stories': Story,
            'Essays': Essay,
            'Images': Image
        }

        self.stdout.write('\n📝 Content:')
        total_content = 0
        for name, model in content_models.items():
            if hasattr(model, 'all_objects'):
                total = model.all_objects.count()
                active = model.objects.count()
                deleted = total - active
                total_content += active
                self.stdout.write(f'   {name}: {active} active, {deleted} deleted')
            else:
                count = model.objects.count()
                total_content += count
                self.stdout.write(f'   {name}: {count}')

        self.stdout.write(f'\n📊 Total Active Content: {total_content} items')

        # Tags and Links
        if hasattr(Tag, 'objects'):
            tag_count = Tag.objects.count()
            self.stdout.write(f'\n🏷️  Tags: {tag_count}')

        if hasattr(ContentLink, 'objects'):
            link_count = ContentLink.objects.count()
            self.stdout.write(f'🔗 Links: {link_count}')

        # Recent activity
        recent_worlds = World.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        self.stdout.write(f'\n📈 Recent Activity (last 7 days):')
        self.stdout.write(f'   New worlds: {recent_worlds}')

    def _show_worlds(self, options):
        """Show worlds list."""
        worlds = World.objects.all().order_by('-created_at')
        
        if options['search']:
            worlds = worlds.filter(title__icontains=options['search'])
        
        limit = options['limit']
        total = worlds.count()
        
        self.stdout.write(self.style.SUCCESS(f'🌍 Worlds ({total} total, showing {min(limit, total)}):'))
        self.stdout.write('=' * 80)

        for world in worlds[:limit]:
            # Count content in this world
            content_count = 0
            for model in [Page, Character, Story, Essay, Image]:
                if hasattr(model, 'objects'):
                    content_count += model.objects.filter(world=world).count()

            visibility = "🌐 Public" if world.is_public else "🔒 Private"
            created = world.created_at.strftime('%Y-%m-%d %H:%M')
            
            self.stdout.write(
                f'ID: {world.id:3d} | {visibility} | "{world.title[:40]}" | '
                f'Creator: {world.creator.username} | Content: {content_count:3d} | '
                f'Created: {created}'
            )

        if total > limit:
            self.stdout.write(f'\n... and {total - limit} more worlds')

    def _show_content(self, options):
        """Show content list."""
        content_type = options.get('content_type')
        world_id = options.get('world')
        include_deleted = options.get('include_deleted', False)
        
        if content_type:
            model_map = {
                'page': Page,
                'character': Character,
                'story': Story,
                'essay': Essay,
                'image': Image
            }
            models = [(content_type.capitalize() + 's', model_map[content_type])]
        else:
            models = [
                ('Pages', Page),
                ('Characters', Character),
                ('Stories', Story),
                ('Essays', Essay),
                ('Images', Image)
            ]

        for name, model in models:
            if include_deleted and hasattr(model, 'all_objects'):
                queryset = model.all_objects.all()
            else:
                queryset = model.objects.all()
            
            if world_id:
                queryset = queryset.filter(world_id=world_id)
            
            if options['search']:
                queryset = queryset.filter(title__icontains=options['search'])
            
            queryset = queryset.order_by('-created_at')
            total = queryset.count()
            limit = options['limit']
            
            if total == 0:
                continue
                
            self.stdout.write(self.style.SUCCESS(f'\n📝 {name} ({total} total, showing {min(limit, total)}):'))
            self.stdout.write('-' * 80)

            for item in queryset[:limit]:
                created = item.created_at.strftime('%Y-%m-%d %H:%M')
                world_title = item.world.title[:20] if item.world else 'No World'
                
                status = ""
                if hasattr(item, 'is_deleted') and item.is_deleted:
                    status = " [DELETED]"
                
                self.stdout.write(
                    f'ID: {item.id:3d} | "{item.title[:40]}" | '
                    f'Author: {item.author.username} | World: {world_title} | '
                    f'Created: {created}{status}'
                )

    def _show_world_detail(self, options):
        """Show detailed world information."""
        world_id = options.get('id')
        if not world_id:
            self.stdout.write(self.style.ERROR('--id is required for world-detail'))
            return

        try:
            world = World.objects.get(id=world_id)
        except World.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'World with ID {world_id} not found'))
            return

        self.stdout.write(self.style.SUCCESS(f'🌍 World Detail: "{world.title}"'))
        self.stdout.write('=' * 60)
        
        self.stdout.write(f'ID: {world.id}')
        self.stdout.write(f'Title: {world.title}')
        self.stdout.write(f'Description: {world.description[:200]}{"..." if len(world.description) > 200 else ""}')
        self.stdout.write(f'Creator: {world.creator.username} ({world.creator.email})')
        self.stdout.write(f'Visibility: {"Public" if world.is_public else "Private"}')
        self.stdout.write(f'Created: {world.created_at}')
        self.stdout.write(f'Updated: {world.updated_at}')

        # Content breakdown
        self.stdout.write('\n📝 Content in this world:')
        content_models = {
            'Pages': Page,
            'Characters': Character,
            'Stories': Story,
            'Essays': Essay,
            'Images': Image
        }

        total_content = 0
        for name, model in content_models.items():
            active_count = model.objects.filter(world=world).count()
            total_content += active_count
            
            if hasattr(model, 'all_objects'):
                total_count = model.all_objects.filter(world=world).count()
                deleted_count = total_count - active_count
                self.stdout.write(f'   {name}: {active_count} active, {deleted_count} deleted')
            else:
                self.stdout.write(f'   {name}: {active_count}')

        self.stdout.write(f'\nTotal active content: {total_content} items')

        # Recent content
        self.stdout.write('\n📅 Recent content (last 5):')
        all_content = []
        
        for model in [Page, Character, Story, Essay, Image]:
            for item in model.objects.filter(world=world).order_by('-created_at')[:5]:
                all_content.append({
                    'type': model.__name__,
                    'title': item.title,
                    'author': item.author.username,
                    'created': item.created_at
                })
        
        all_content.sort(key=lambda x: x['created'], reverse=True)
        
        for item in all_content[:5]:
            created = item['created'].strftime('%Y-%m-%d %H:%M')
            self.stdout.write(f'   {item["type"]}: "{item["title"]}" by {item["author"]} ({created})')

    def _show_stats(self, options):
        """Show database statistics."""
        self.stdout.write(self.style.SUCCESS('📊 Database Statistics'))
        self.stdout.write('=' * 50)

        # User statistics
        users = User.objects.all()
        self.stdout.write(f'\n👥 User Statistics:')
        self.stdout.write(f'   Total users: {users.count()}')
        self.stdout.write(f'   Staff users: {users.filter(is_staff=True).count()}')
        self.stdout.write(f'   Active users (last 30 days): {users.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()}')

        # World statistics
        worlds = World.objects.all()
        self.stdout.write(f'\n🌍 World Statistics:')
        self.stdout.write(f'   Total worlds: {worlds.count()}')
        self.stdout.write(f'   Public worlds: {worlds.filter(is_public=True).count()}')
        self.stdout.write(f'   Private worlds: {worlds.filter(is_public=False).count()}')
        
        # Top world creators
        top_creators = User.objects.annotate(
            world_count=Count('created_worlds')
        ).filter(world_count__gt=0).order_by('-world_count')[:5]
        
        self.stdout.write(f'\n🏆 Top World Creators:')
        for user in top_creators:
            self.stdout.write(f'   {user.username}: {user.world_count} worlds')

        # Content statistics
        self.stdout.write(f'\n📝 Content Statistics:')
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
                self.stdout.write(f'   {name}: {active} active, {deleted} deleted, {total} total')
            else:
                count = model.objects.count()
                self.stdout.write(f'   {name}: {count}')

        # Activity statistics
        self.stdout.write(f'\n📈 Activity Statistics:')
        now = timezone.now()
        
        for days, label in [(1, 'Today'), (7, 'This week'), (30, 'This month')]:
            cutoff = now - timedelta(days=days)
            new_worlds = World.objects.filter(created_at__gte=cutoff).count()
            self.stdout.write(f'   New worlds {label.lower()}: {new_worlds}')

    def _search_content(self, options):
        """Search across all content."""
        search_term = options.get('search')
        if not search_term:
            self.stdout.write(self.style.ERROR('--search is required'))
            return

        self.stdout.write(self.style.SUCCESS(f'🔍 Search Results for: "{search_term}"'))
        self.stdout.write('=' * 60)

        # Search worlds
        worlds = World.objects.filter(
            Q(title__icontains=search_term) | Q(description__icontains=search_term)
        )[:5]
        
        if worlds:
            self.stdout.write(f'\n🌍 Worlds ({worlds.count()}):')
            for world in worlds:
                self.stdout.write(f'   ID: {world.id} | "{world.title}" | {world.creator.username}')

        # Search content
        content_models = {
            'Pages': Page,
            'Characters': Character,
            'Stories': Story,
            'Essays': Essay,
            'Images': Image
        }

        for name, model in content_models.items():
            items = model.objects.filter(
                Q(title__icontains=search_term) | Q(content__icontains=search_term)
            )[:5]
            
            if items:
                self.stdout.write(f'\n📝 {name} ({items.count()}):')
                for item in items:
                    self.stdout.write(f'   ID: {item.id} | "{item.title}" | {item.author.username} | World: {item.world.title}')

    def _show_recent(self, options):
        """Show recent activity."""
        days = 7  # Last 7 days
        cutoff = timezone.now() - timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'📅 Recent Activity (last {days} days)'))
        self.stdout.write('=' * 50)

        # Recent worlds
        recent_worlds = World.objects.filter(created_at__gte=cutoff).order_by('-created_at')
        if recent_worlds:
            self.stdout.write(f'\n🌍 New Worlds ({recent_worlds.count()}):')
            for world in recent_worlds:
                created = world.created_at.strftime('%Y-%m-%d %H:%M')
                self.stdout.write(f'   "{world.title}" by {world.creator.username} ({created})')

        # Recent content
        all_recent = []
        content_models = {
            'Page': Page,
            'Character': Character,
            'Story': Story,
            'Essay': Essay,
            'Image': Image
        }

        for name, model in content_models.items():
            for item in model.objects.filter(created_at__gte=cutoff):
                all_recent.append({
                    'type': name,
                    'title': item.title,
                    'author': item.author.username,
                    'world': item.world.title,
                    'created': item.created_at
                })

        all_recent.sort(key=lambda x: x['created'], reverse=True)
        
        if all_recent:
            self.stdout.write(f'\n📝 New Content ({len(all_recent)}):')
            for item in all_recent[:10]:
                created = item['created'].strftime('%Y-%m-%d %H:%M')
                self.stdout.write(f'   {item["type"]}: "{item["title"]}" by {item["author"]} in "{item["world"]}" ({created})')

    def _show_empty_worlds(self, options):
        """Show worlds with no content."""
        self.stdout.write(self.style.SUCCESS('🌍 Empty Worlds'))
        self.stdout.write('=' * 40)

        empty_worlds = []
        for world in World.objects.all():
            content_count = 0
            for model in [Page, Character, Story, Essay, Image]:
                content_count += model.objects.filter(world=world).count()
            
            if content_count == 0:
                empty_worlds.append((world, content_count))

        if not empty_worlds:
            self.stdout.write('No empty worlds found.')
            return

        self.stdout.write(f'Found {len(empty_worlds)} empty worlds:')
        for world, count in empty_worlds:
            created = world.created_at.strftime('%Y-%m-%d')
            self.stdout.write(f'   ID: {world.id} | "{world.title}" | Creator: {world.creator.username} | Created: {created}')

    def _show_orphaned_content(self, options):
        """Show content that might be orphaned."""
        self.stdout.write(self.style.SUCCESS('🔗 Orphaned Content Analysis'))
        self.stdout.write('=' * 50)

        # This would need ContentLink model to be fully implemented
        self.stdout.write('Note: Full orphaned content analysis requires ContentLink model.')
        
        # For now, show content in worlds that no longer exist
        content_models = {
            'Pages': Page,
            'Characters': Character,
            'Stories': Story,
            'Essays': Essay,
            'Images': Image
        }

        for name, model in content_models.items():
            # This is a basic check - in a real scenario you'd check for broken links
            orphaned = model.objects.filter(world__isnull=True) if hasattr(model.objects.first(), 'world') else []
            
            if orphaned:
                self.stdout.write(f'\n{name} without worlds: {orphaned.count()}')
                for item in orphaned[:5]:
                    self.stdout.write(f'   ID: {item.id} | "{item.title}" | Author: {item.author.username}')