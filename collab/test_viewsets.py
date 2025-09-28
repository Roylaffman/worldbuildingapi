"""
Unit tests for ViewSets in the collaborative worldbuilding application.
Tests API functionality, permissions, and business logic.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import World, Page, Essay, Character, Story, Image, Tag
from .permissions import IsCreatorOrReadOnly, IsAuthorOrReadOnly


class WorldViewSetTest(TestCase):
    """Test WorldViewSet functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user1
        )
    
    def test_world_list_authenticated(self):
        """Test listing worlds requires authentication."""
        # Unauthenticated request should fail
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticated request should succeed
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_world_creation(self):
        """Test world creation functionality."""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'title': 'New World',
            'description': 'A new world for testing',
            'is_public': True
        }
        
        response = self.client.post('/api/worlds/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that creator is automatically set
        self.assertEqual(response.data['creator']['username'], 'creator')
    
    def test_world_detail_view(self):
        """Test world detail view functionality."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include detailed information
        self.assertIn('content_counts', response.data)
        self.assertIn('collaboration_stats', response.data)
        self.assertIn('top_contributors', response.data)
    
    def test_world_update_permissions(self):
        """Test world update permissions (creator only)."""
        # Creator should be able to update
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Updated World Title'}
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Other user should not be able to update
        self.client.force_authenticate(user=self.user2)
        data = {'title': 'Unauthorized Update'}
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_world_contributors_endpoint(self):
        """Test world contributors endpoint."""
        # Create some content by different users
        Page.objects.create(
            title='Page by Creator',
            content='Content by creator',
            author=self.user1,
            world=self.world
        )
        Page.objects.create(
            title='Page by Other',
            content='Content by other user',
            author=self.user2,
            world=self.world
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/worlds/{self.world.id}/contributors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include contributor information
        self.assertIn('contributors', response.data)
        self.assertIn('collaboration_summary', response.data)
        self.assertEqual(response.data['total_contributors'], 2)
    
    def test_world_timeline_endpoint(self):
        """Test world timeline endpoint."""
        # Create some content
        Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user1,
            world=self.world
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/worlds/{self.world.id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include timeline data
        self.assertIn('timeline', response.data)
        self.assertIn('pagination', response.data)
        self.assertEqual(len(response.data['timeline']), 1)
    
    def test_world_search_endpoint(self):
        """Test world search endpoint."""
        # Create some content
        Page.objects.create(
            title='Searchable Page',
            content='This content can be searched',
            author=self.user1,
            world=self.world
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/worlds/{self.world.id}/search/', {'q': 'searchable'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include search results
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_world_statistics_endpoint(self):
        """Test world statistics endpoint."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/worlds/{self.world.id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include statistics
        self.assertIn('content_counts', response.data)
        self.assertIn('contributor_count', response.data)
        self.assertIn('popular_tags', response.data)
        self.assertIn('recent_activity', response.data)


class ContentViewSetTest(TestCase):
    """Test content ViewSet functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='author1',
            email='author1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='author2',
            email='author2@example.com',
            password='testpass123'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user1
        )
    
    def test_page_creation(self):
        """Test page creation functionality."""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'title': 'Test Page',
            'content': 'This is test content for the page',
            'summary': 'Test summary'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that author is automatically set
        self.assertEqual(response.data['author']['username'], 'author1')
        
        # Check that world is automatically set
        self.assertEqual(response.data['world'], self.world.id)
    
    def test_page_creation_with_tags(self):
        """Test page creation with tags."""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'title': 'Test Page',
            'content': 'This is test content for the page',
            'summary': 'Test summary',
            'tags': ['fantasy', 'adventure', 'magic']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that tags were added
        page_id = response.data['id']
        page = Page.objects.get(id=page_id)
        tags = page.get_tags()
        tag_names = [tag.name for tag in tags]
        
        self.assertIn('fantasy', tag_names)
        self.assertIn('adventure', tag_names)
        self.assertIn('magic', tag_names)
    
    def test_page_immutability_enforcement(self):
        """Test that pages cannot be updated after creation."""
        self.client.force_authenticate(user=self.user1)
        
        # Create page
        data = {
            'title': 'Test Page',
            'content': 'Original content',
            'summary': 'Original summary'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        page_id = response.data['id']
        
        # Try to update page (should fail)
        update_data = {'title': 'Updated Title'}
        response = self.client.put(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to patch page (should fail)
        response = self.client.patch(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete page (should fail)
        response = self.client.delete(f'/api/worlds/{self.world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_page_list_filtering(self):
        """Test page list filtering functionality."""
        # Create test pages
        Page.objects.create(
            title='Fantasy Page',
            content='Fantasy content',
            author=self.user1,
            world=self.world,
            summary='Fantasy summary'
        )
        Page.objects.create(
            title='Adventure Page',
            content='Adventure content',
            author=self.user2,
            world=self.world,
            summary='Adventure summary'
        )
        
        self.client.force_authenticate(user=self.user1)
        
        # Test author filtering
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/', {'author': 'author1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author']['username'], 'author1')
        
        # Test search filtering
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/', {'search': 'fantasy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Fantasy Page')
    
    def test_add_tags_endpoint(self):
        """Test adding tags to existing content."""
        # Create page
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user1,
            world=self.world
        )
        
        self.client.force_authenticate(user=self.user1)
        
        # Add tags
        data = {'tags': ['new-tag', 'another-tag']}
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/{page.id}/add-tags/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response
        self.assertEqual(len(response.data['added_tags']), 2)
        self.assertIn('new-tag', response.data['added_tags'])
        self.assertIn('another-tag', response.data['added_tags'])
    
    def test_add_links_endpoint(self):
        """Test adding links to existing content."""
        # Create pages
        page1 = Page.objects.create(
            title='Page 1',
            content='Content 1',
            author=self.user1,
            world=self.world
        )
        page2 = Page.objects.create(
            title='Page 2',
            content='Content 2',
            author=self.user1,
            world=self.world
        )
        
        self.client.force_authenticate(user=self.user1)
        
        # Add link
        data = {
            'links': [
                {
                    'content_type': 'page',
                    'content_id': page2.id
                }
            ]
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/{page1.id}/add-links/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response
        self.assertEqual(len(response.data['added_links']), 1)
        self.assertEqual(response.data['added_links'][0]['target_id'], page2.id)
    
    def test_attribution_details_endpoint(self):
        """Test attribution details endpoint."""
        # Create content with links
        page1 = Page.objects.create(
            title='Page 1',
            content='Content 1',
            author=self.user1,
            world=self.world
        )
        page2 = Page.objects.create(
            title='Page 2',
            content='Content 2',
            author=self.user2,
            world=self.world
        )
        
        # Create link
        page1.link_to(page2)
        
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/{page1.id}/attribution_details/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('content', response.data)
        self.assertIn('attribution', response.data)
        self.assertIn('collaboration_metrics', response.data)
        self.assertIn('attribution_suggestions', response.data)


class EssayViewSetTest(TestCase):
    """Test EssayViewSet specific functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
    
    def test_essay_creation(self):
        """Test essay creation functionality."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Test Essay',
            'content': 'This is test content for the essay with many words to test word count calculation.',
            'abstract': 'Test abstract'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/essays/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that word count is calculated
        self.assertGreater(response.data['word_count'], 0)
    
    def test_essay_word_count_filtering(self):
        """Test essay filtering by word count."""
        # Create essays with different word counts
        Essay.objects.create(
            title='Short Essay',
            content='Short content.',
            author=self.user,
            world=self.world
        )
        Essay.objects.create(
            title='Long Essay',
            content='This is a much longer essay with many more words to increase the word count significantly.',
            author=self.user,
            world=self.world
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Test minimum word count filter
        response = self.client.get(f'/api/worlds/{self.world.id}/essays/', {'min_words': '10'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only long essay should match


class CharacterViewSetTest(TestCase):
    """Test CharacterViewSet specific functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
    
    def test_character_creation(self):
        """Test character creation functionality."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Test Character',
            'content': 'Character description',
            'full_name': 'John Doe',
            'species': 'Human',
            'occupation': 'Adventurer',
            'personality_traits': ['brave', 'kind'],
            'relationships': {'friend': 'Alice'}
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/characters/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check character-specific fields
        self.assertEqual(response.data['full_name'], 'John Doe')
        self.assertEqual(response.data['species'], 'Human')
        self.assertEqual(response.data['personality_traits'], ['brave', 'kind'])
    
    def test_character_filtering(self):
        """Test character filtering functionality."""
        # Create characters with different attributes
        Character.objects.create(
            title='Human Character',
            content='Human description',
            author=self.user,
            world=self.world,
            full_name='John Human',
            species='Human',
            occupation='Warrior'
        )
        Character.objects.create(
            title='Elf Character',
            content='Elf description',
            author=self.user,
            world=self.world,
            full_name='Elara Elf',
            species='Elf',
            occupation='Mage'
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Test species filtering
        response = self.client.get(f'/api/worlds/{self.world.id}/characters/', {'species': 'Human'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['species'], 'Human')
        
        # Test occupation filtering
        response = self.client.get(f'/api/worlds/{self.world.id}/characters/', {'occupation': 'Mage'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['occupation'], 'Mage')


class StoryViewSetTest(TestCase):
    """Test StoryViewSet specific functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
    
    def test_story_creation(self):
        """Test story creation functionality."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Test Story',
            'content': 'This is a test story with some content.',
            'genre': 'Fantasy',
            'story_type': 'short_story',
            'main_characters': ['Hero', 'Villain']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/stories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check story-specific fields
        self.assertEqual(response.data['genre'], 'Fantasy')
        self.assertEqual(response.data['story_type'], 'short_story')
        self.assertEqual(response.data['main_characters'], ['Hero', 'Villain'])
        
        # Check word count is calculated
        self.assertGreater(response.data['word_count'], 0)
    
    def test_story_filtering(self):
        """Test story filtering functionality."""
        # Create stories with different attributes
        Story.objects.create(
            title='Fantasy Story',
            content='Fantasy story content',
            author=self.user,
            world=self.world,
            genre='Fantasy',
            is_canonical=True
        )
        Story.objects.create(
            title='Sci-Fi Story',
            content='Sci-fi story content',
            author=self.user,
            world=self.world,
            genre='Science Fiction',
            is_canonical=False
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Test genre filtering
        response = self.client.get(f'/api/worlds/{self.world.id}/stories/', {'genre': 'Fantasy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['genre'], 'Fantasy')
        
        # Test canonical filtering
        response = self.client.get(f'/api/worlds/{self.world.id}/stories/', {'is_canonical': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_canonical'])


class PermissionTest(TestCase):
    """Test permission classes functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='testpass123'
        )
        self.other = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.creator
        )
        
        # Create test content
        self.page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.author,
            world=self.world
        )
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        # World list should require authentication
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Content creation should require authentication
        data = {'title': 'Test', 'content': 'Test content'}
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_world_creator_permissions(self):
        """Test IsCreatorOrReadOnly permission for worlds."""
        # Creator should be able to update
        self.client.force_authenticate(user=self.creator)
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Non-creator should not be able to update
        self.client.force_authenticate(user=self.other)
        data = {'title': 'Unauthorized Update'}
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # But non-creator should be able to read
        response = self.client.get(f'/api/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_content_author_permissions(self):
        """Test IsAuthorOrReadOnly permission for content."""
        # Anyone should be able to read content
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/{self.page.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # But content is immutable, so no one should be able to update
        # (This is enforced by the immutability system, not just permissions)
        self.client.force_authenticate(user=self.author)
        data = {'title': 'Updated Title'}
        response = self.client.put(f'/api/worlds/{self.world.id}/pages/{self.page.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_content_creation_permissions(self):
        """Test that authenticated users can create content."""
        self.client.force_authenticate(user=self.other)
        
        data = {
            'title': 'New Page',
            'content': 'New content by other user',
            'summary': 'New summary'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Author should be automatically set
        self.assertEqual(response.data['author']['username'], 'other')


class PaginationTest(TestCase):
    """Test pagination functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
        
        # Create multiple pages for pagination testing
        for i in range(25):
            Page.objects.create(
                title=f'Page {i}',
                content=f'Content for page {i}',
                author=self.user,
                world=self.world
            )
    
    def test_page_list_pagination(self):
        """Test that page lists are properly paginated."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be paginated (default page size is typically 20)
        if hasattr(response.data, 'get'):
            # Paginated response
            self.assertIn('results', response.data)
            self.assertIn('count', response.data)
            self.assertIn('next', response.data)
            self.assertIn('previous', response.data)
        else:
            # Non-paginated response (depends on configuration)
            self.assertIsInstance(response.data, list)


class ErrorHandlingTest(TestCase):
    """Test error handling in ViewSets."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
    
    def test_invalid_world_id(self):
        """Test handling of invalid world IDs."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/worlds/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_content_data(self):
        """Test handling of invalid content data."""
        self.client.force_authenticate(user=self.user)
        
        # Test with invalid data
        data = {
            'title': '',  # Empty title should fail validation
            'content': 'Valid content'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.data).lower())
    
    def test_cross_world_content_access(self):
        """Test that content from one world cannot be accessed via another world's endpoint."""
        # Create another world
        other_world = World.objects.create(
            title='Other World',
            description='Another world',
            creator=self.user
        )
        
        # Create page in first world
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Try to access page via other world's endpoint
        response = self.client.get(f'/api/worlds/{other_world.id}/pages/{page.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)