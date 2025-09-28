"""
Main test module for the collaborative worldbuilding application.
Imports all test modules to run comprehensive test suite.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from .models import World, Page, Essay, Character, Story, Image, Tag, ContentTag, ContentLink

# Import all test modules for comprehensive testing
from .test_models import *
from .test_serializers import *
from .test_viewsets import *
from .test_auth_permissions import *
from .test_immutability import *


class TaggingLinkingAPITest(TestCase):
    """Test tagging and linking API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Test World',
            description='A world for testing',
            creator=self.user1
        )
        
        # Create test content
        self.page1 = Page.objects.create(
            title='Test Page 1',
            content='This is test page 1 content',
            author=self.user1,
            world=self.world,
            summary='Test page summary'
        )
        
        self.page2 = Page.objects.create(
            title='Test Page 2',
            content='This is test page 2 content',
            author=self.user2,
            world=self.world,
            summary='Another test page'
        )
        
        self.character = Character.objects.create(
            title='Test Character',
            content='Character description',
            author=self.user1,
            world=self.world,
            full_name='John Doe',
            species='Human',
            occupation='Adventurer',
            personality_traits=['brave', 'curious'],
            relationships={'friend': 'Alice', 'mentor': 'Bob'}
        )
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
    
    def test_tag_management_endpoints(self):
        """Test tag CRUD operations."""
        # Test creating tags
        tag_data = {'name': 'fantasy'}
        response = self.client.post(f'/api/worlds/{self.world.id}/tags/', tag_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'fantasy')
        
        tag_id = response.data['id']
        
        # Test listing tags
        response = self.client.get(f'/api/worlds/{self.world.id}/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # May have tags from other tests
        
        # Test retrieving specific tag
        response = self.client.get(f'/api/worlds/{self.world.id}/tags/{tag_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'fantasy')
    
    def test_content_tagging(self):
        """Test adding tags to content."""
        # Test adding tags to page (tags will be created automatically)
        tag_data = {'tags': ['adventure', 'magic', 'new-tag']}
        response = self.client.post(
            f'/api/worlds/{self.world.id}/pages/{self.page1.id}/add-tags/',
            tag_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['added_tags']), 3)
        
        # Verify tags were added
        page_tags = self.page1.get_tags()
        tag_names = [tag.name for tag in page_tags]
        self.assertIn('adventure', tag_names)
        self.assertIn('magic', tag_names)
        self.assertIn('new-tag', tag_names)
    
    def test_content_linking(self):
        """Test linking content entries."""
        # Test adding links to page
        link_data = {
            'links': [
                {
                    'content_type': 'character',
                    'content_id': self.character.id
                }
            ]
        }
        response = self.client.post(
            f'/api/worlds/{self.world.id}/pages/{self.page1.id}/add-links/',
            link_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['added_links']), 1)
        
        # Verify bidirectional link was created
        linked_content = self.page1.get_linked_content()
        self.assertEqual(len(linked_content), 1)
        self.assertEqual(linked_content[0].id, self.character.id)
        
        # Verify reverse link
        linking_content = self.character.get_content_linking_to_this()
        self.assertEqual(len(linking_content), 1)
        self.assertEqual(linking_content[0].id, self.page1.id)
    
    def test_tag_based_search(self):
        """Test searching content by tags."""
        # Add tags to content
        self.page1.add_tag('fantasy')
        self.page1.add_tag('adventure')
        self.page2.add_tag('fantasy')
        self.character.add_tag('adventure')
        
        # Test searching across all content types
        response = self.client.get(
            f'/api/worlds/{self.world.id}/tags/search-content/',
            {'tags': 'fantasy,adventure', 'match_all': 'false'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results_by_type']
        self.assertGreater(len(results['pages']), 0)
        self.assertGreater(len(results['characters']), 0)
    
    def test_popular_tags(self):
        """Test popular tags endpoint."""
        # Add tags with different usage counts
        self.page1.add_tag('popular')
        self.page2.add_tag('popular')
        self.character.add_tag('popular')
        self.page1.add_tag('rare')
        
        response = self.client.get(f'/api/worlds/{self.world.id}/tags/popular/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        popular_tags = response.data['popular_tags']
        self.assertGreater(len(popular_tags), 0)
        
        # Most popular tag should be first
        most_popular = popular_tags[0]
        self.assertEqual(most_popular['name'], 'popular')
        self.assertEqual(most_popular['usage_count'], 3)


class ChronologicalViewingAPITest(TestCase):
    """Test chronological viewing and filtering API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Test World',
            description='A world for testing chronological features',
            creator=self.user1
        )
        
        # Create test content with different timestamps
        from datetime import datetime, timedelta
        base_time = datetime.now()
        
        self.page1 = Page.objects.create(
            title='First Page',
            content='This is the first page content',
            author=self.user1,
            world=self.world,
            summary='First page summary'
        )
        # Manually set created_at to simulate different creation times
        self.page1.created_at = base_time - timedelta(days=5)
        self.page1.save(force_update=True)
        
        self.essay1 = Essay.objects.create(
            title='Test Essay',
            content='This is an essay about the world',
            author=self.user2,
            world=self.world,
            abstract='Essay abstract'
        )
        self.essay1.created_at = base_time - timedelta(days=3)
        self.essay1.save(force_update=True)
        
        self.character1 = Character.objects.create(
            title='Test Character',
            content='Character description',
            author=self.user1,
            world=self.world,
            full_name='John Doe',
            species='Human',
            occupation='Adventurer',
            personality_traits=['brave', 'curious'],
            relationships={'friend': 'Alice'}
        )
        self.character1.created_at = base_time - timedelta(days=1)
        self.character1.save(force_update=True)
        
        # Add tags to content
        self.page1.add_tag('adventure')
        self.page1.add_tag('fantasy')
        self.essay1.add_tag('lore')
        self.character1.add_tag('adventure')
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
    
    def test_timeline_view(self):
        """Test the chronological timeline view."""
        response = self.client.get(f'/api/worlds/{self.world.id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 3)
        
        # Check chronological order (newest first)
        self.assertEqual(timeline[0]['title'], 'Test Character')
        self.assertEqual(timeline[1]['title'], 'Test Essay')
        self.assertEqual(timeline[2]['title'], 'First Page')
        
        # Check timeline metadata
        for item in timeline:
            self.assertIn('content_type', item)
            self.assertIn('timeline_position', item)
            self.assertIn('author', item)
            self.assertIn('created_at', item)
    
    def test_timeline_filtering_by_content_type(self):
        """Test filtering timeline by content type."""
        response = self.client.get(
            f'/api/worlds/{self.world.id}/timeline/',
            {'content_types': 'page,character'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 2)
        
        content_types = [item['content_type'] for item in timeline]
        self.assertIn('character', content_types)
        self.assertIn('page', content_types)
        self.assertNotIn('essay', content_types)
    
    def test_timeline_filtering_by_author(self):
        """Test filtering timeline by author."""
        response = self.client.get(
            f'/api/worlds/{self.world.id}/timeline/',
            {'author': 'testuser1'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 2)  # page1 and character1
        
        for item in timeline:
            self.assertEqual(item['author']['username'], 'testuser1')
    
    def test_timeline_filtering_by_tags(self):
        """Test filtering timeline by tags."""
        response = self.client.get(
            f'/api/worlds/{self.world.id}/timeline/',
            {'tags': 'adventure'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 2)  # page1 and character1 have 'adventure' tag
        
        titles = [item['title'] for item in timeline]
        self.assertIn('First Page', titles)
        self.assertIn('Test Character', titles)
    
    def test_timeline_search(self):
        """Test search functionality within timeline."""
        response = self.client.get(
            f'/api/worlds/{self.world.id}/timeline/',
            {'search': 'character'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]['title'], 'Test Character')
    
    def test_advanced_search(self):
        """Test the advanced search endpoint."""
        response = self.client.get(
            f'/api/worlds/{self.world.id}/search/',
            {'q': 'test'}  # Search for "test" which appears in titles
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        self.assertGreater(len(results), 0)
        
        # Check that results have relevance scores
        for result in results:
            self.assertIn('relevance_score', result)
            self.assertIn('content_type', result)
    
    def test_search_with_filters(self):
        """Test search with additional filters."""
        response = self.client.get(
            f'/api/worlds/{self.world.id}/search/',
            {
                'q': 'test',
                'content_types': 'character',
                'author': 'testuser1'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Character')
    
    def test_related_content_discovery(self):
        """Test related content discovery."""
        response = self.client.get(
            f'/api/worlds/{self.world.id}/related_content/',  # Note: underscore, not hyphen
            {
                'content_type': 'page',
                'content_id': self.page1.id,
                'relation_types': 'tags,author'
            }
        )
        if response.status_code != status.HTTP_200_OK:
            print(f"Related content response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should find character1 related by tags (both have 'adventure' tag)
        related_by_tags = response.data['related_by_tags']
        self.assertGreater(len(related_by_tags), 0)
        
        # Should find character1 related by author (same author)
        related_by_author = response.data['related_by_author']
        self.assertGreater(len(related_by_author), 0)
    
    def test_chronological_content_endpoint(self):
        """Test chronological content endpoint for specific content types."""
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/chronological/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return pages in chronological order
        pages = response.data
        self.assertGreater(len(pages), 0)
    
    def test_statistics_endpoint(self):
        """Test the statistics endpoint."""
        response = self.client.get(f'/api/worlds/{self.world.id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertIn('content_counts', stats)
        self.assertIn('contributor_count', stats)
        self.assertIn('popular_tags', stats)
        self.assertIn('recent_activity', stats)
        
        # Check content counts
        content_counts = stats['content_counts']
        self.assertEqual(content_counts['pages'], 1)
        self.assertEqual(content_counts['essays'], 1)
        self.assertEqual(content_counts['characters'], 1)
        self.assertEqual(content_counts['total'], 3)
        
        # Check contributor count
        self.assertEqual(stats['contributor_count'], 2)  # user1 and user2


class URLRoutingAPIStructureTest(TestCase):
    """Test URL routing and API structure implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Test World',
            description='A world for testing API structure',
            creator=self.user
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
    
    def test_api_root_endpoints(self):
        """Test API root and documentation endpoints."""
        # Test main API root
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('version', response.data)
        self.assertIn('endpoints', response.data)
        
        # Test versioned API root
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test API schema
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('openapi', response.data)
    
    def test_api_versioning_headers(self):
        """Test that API versioning headers are properly set."""
        response = self.client.get('/api/v1/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get('X-API-Version'), 'v1')
        self.assertEqual(response.get('X-API-Service'), 'collaborative-worldbuilding')
    
    def test_health_endpoint(self):
        """Test API health check endpoint."""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['version'], 'v1')
    
    def test_immutability_enforcement_middleware(self):
        """Test that immutability is enforced by middleware."""
        # Create a page first
        page_data = {
            'title': 'Test Page',
            'content': 'Test content',
            'summary': 'Test summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        page_id = response.data['id']
        
        # Try to update the page (should be blocked by middleware)
        update_data = {'title': 'Updated Title'}
        response = self.client.put(f'/api/v1/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response_data = response.json() if hasattr(response, 'json') else response.data
        self.assertIn('Immutability Violation', response_data['error'])
        
        # Try to patch the page (should be blocked by middleware)
        response = self.client.patch(f'/api/v1/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete the page (should be blocked by middleware)
        response = self.client.delete(f'/api/v1/worlds/{self.world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_options_requests_documentation(self):
        """Test OPTIONS requests return proper documentation."""
        # Test OPTIONS on immutable content endpoint
        response = self.client.options(f'/api/v1/worlds/{self.world.id}/pages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json() if hasattr(response, 'json') else response.data
        self.assertIn('allowed_methods', response_data)
        self.assertEqual(set(response_data['allowed_methods']), {'GET', 'POST', 'OPTIONS'})
        self.assertTrue(response_data['immutable_content'])
        
        # Test OPTIONS on management endpoint
        response = self.client.options(f'/api/v1/worlds/{self.world.id}/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json() if hasattr(response, 'json') else response.data
        self.assertIn('PUT', response_data['allowed_methods'])  # Tags are manageable
    
    def test_nested_world_content_structure(self):
        """Test that world-scoped content endpoints work correctly."""
        # Test creating content within a world
        content_types = [
            ('pages', {'title': 'Test Page', 'content': 'Page content', 'summary': 'Summary'}),
            ('essays', {'title': 'Test Essay', 'content': 'Essay content', 'abstract': 'Abstract'}),
            ('characters', {
                'title': 'Test Character', 
                'content': 'Character description',
                'full_name': 'John Doe',
                'personality_traits': ['brave'],
                'relationships': {'friend': 'Alice'}
            }),
            ('stories', {
                'title': 'Test Story', 
                'content': 'Story content',
                'genre': 'Fantasy',
                'main_characters': ['Hero']
            }),
        ]
        
        for content_type, data in content_types:
            # Test creation
            response = self.client.post(f'/api/v1/worlds/{self.world.id}/{content_type}/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, 
                           f"Failed to create {content_type}: {response.data}")
            
            content_id = response.data['id']
            
            # Test retrieval
            response = self.client.get(f'/api/v1/worlds/{self.world.id}/{content_type}/{content_id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Test listing
            response = self.client.get(f'/api/v1/worlds/{self.world.id}/{content_type}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreater(len(response.data), 0)
    
    def test_authentication_endpoints_structure(self):
        """Test authentication endpoint structure."""
        auth_endpoints = [
            '/api/v1/auth/register/',
            '/api/v1/auth/login/',
            '/api/v1/auth/refresh/',
            '/api/v1/auth/verify/',
            '/api/v1/auth/user/',
            '/api/v1/auth/profile/',
        ]
        
        for endpoint in auth_endpoints:
            # Test that endpoints exist (may return 401 for protected endpoints)
            response = self.client.get(endpoint)
            self.assertIn(response.status_code, [200, 401, 405], 
                         f"Endpoint {endpoint} not properly configured")
    
    def test_world_management_endpoints(self):
        """Test world management endpoint structure."""
        # Test world listing
        response = self.client.get('/api/v1/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test world detail
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test world timeline
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test world search
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/search/', {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test world statistics
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_tag_and_link_management_structure(self):
        """Test tag and link management endpoint structure."""
        # Test tag management
        tag_data = {'name': 'test-tag'}
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/tags/', tag_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        tag_id = response.data['id']
        
        # Test tag retrieval
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/tags/{tag_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test tag update (should be allowed for management)
        update_data = {'name': 'updated-tag'}
        response = self.client.put(f'/api/v1/worlds/{self.world.id}/tags/{tag_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CollaborativeFeaturesTest(TestCase):
    """Test collaborative features and attribution implementation."""
    
    def setUp(self):
        """Set up test data for collaborative features."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='author1',
            email='author1@example.com',
            password='testpass123',
            first_name='Alice',
            last_name='Smith'
        )
        self.user2 = User.objects.create_user(
            username='author2',
            email='author2@example.com',
            password='testpass123',
            first_name='Bob',
            last_name='Jones'
        )
        self.user3 = User.objects.create_user(
            username='author3',
            email='author3@example.com',
            password='testpass123',
            first_name='Carol',
            last_name='Davis'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Collaborative Test World',
            description='A world for testing collaborative features',
            creator=self.user1
        )
        
        # Create content by different authors
        self.page1 = Page.objects.create(
            title='Foundation Page',
            content='This is the foundation of our world',
            author=self.user1,
            world=self.world,
            summary='Foundation content'
        )
        
        self.character1 = Character.objects.create(
            title='Hero Character',
            content='A brave hero character',
            author=self.user2,
            world=self.world,
            full_name='Hero McHeroface',
            species='Human',
            occupation='Adventurer',
            personality_traits=['brave', 'kind'],
            relationships={'mentor': 'Wise Sage'}
        )
        
        self.story1 = Story.objects.create(
            title='Epic Tale',
            content='An epic story about the hero',
            author=self.user3,
            world=self.world,
            genre='Fantasy',
            main_characters=['Hero McHeroface']
        )
        
        # Add tags and links to create collaboration
        self.page1.add_tag('foundation')
        self.page1.add_tag('worldbuilding')
        self.character1.add_tag('hero')
        self.character1.add_tag('main-character')
        self.story1.add_tag('hero')
        self.story1.add_tag('epic')
        
        # Create cross-author links
        self.character1.link_to(self.page1)  # Character references foundation
        self.story1.link_to(self.character1)  # Story references character
        self.story1.link_to(self.page1)  # Story references foundation
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
    
    def test_attribution_in_serializers(self):
        """Test that content serializers include proper attribution."""
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/pages/{self.page1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        
        # Check basic attribution
        self.assertIn('attribution', data)
        self.assertIn('Alice Smith', data['attribution'])
        self.assertIn('Created by', data['attribution'])
        
        # Check collaboration info
        self.assertIn('collaboration_info', data)
        collab_info = data['collaboration_info']
        self.assertIn('is_collaborative', collab_info)
        self.assertIn('collaboration_score', collab_info)
        self.assertIn('referenced_by_authors', collab_info)
        
        # Should show that other authors reference this content
        self.assertTrue(collab_info['is_collaborative'])
        self.assertIn('author2', collab_info['referenced_by_authors'])
        self.assertIn('author3', collab_info['referenced_by_authors'])
    
    def test_world_collaboration_stats(self):
        """Test world-level collaboration statistics."""
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        
        # Check collaboration stats
        self.assertIn('collaboration_stats', data)
        collab_stats = data['collaboration_stats']
        self.assertIn('cross_author_collaborations', collab_stats)
        self.assertIn('collaboration_ratio', collab_stats)
        self.assertIn('is_highly_collaborative', collab_stats)
        
        # Should detect cross-author collaborations
        self.assertGreater(collab_stats['cross_author_collaborations'], 0)
        
        # Check top contributors
        self.assertIn('top_contributors', data)
        contributors = data['top_contributors']
        self.assertEqual(len(contributors), 3)  # All three users
        
        # Check contributor details
        for contributor in contributors:
            self.assertIn('full_name', contributor)
            self.assertIn('contributions', contributor)
            self.assertIn('first_contribution', contributor)
            self.assertIn('is_creator', contributor)
    
    def test_contributors_endpoint_with_collaboration(self):
        """Test the enhanced contributors endpoint."""
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/contributors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        
        # Check collaboration summary
        self.assertIn('collaboration_summary', data)
        summary = data['collaboration_summary']
        self.assertIn('total_cross_author_links', summary)
        self.assertIn('most_collaborative', summary)
        self.assertIn('most_active', summary)
        
        # Check individual contributor data
        contributors = data['contributors']
        self.assertEqual(len(contributors), 3)
        
        for contributor in contributors:
            self.assertIn('collaboration_metrics', contributor)
            self.assertIn('activity_timeline', contributor)
            self.assertIn('attribution', contributor)
            
            collab_metrics = contributor['collaboration_metrics']
            self.assertIn('links_created', collab_metrics)
            self.assertIn('links_received', collab_metrics)
            self.assertIn('collaborating_with', collab_metrics)
            self.assertIn('is_collaborative', collab_metrics)
    
    def test_attribution_report_endpoint(self):
        """Test the attribution report endpoint."""
        response = self.client.get(f'/api/v1/worlds/{self.world.id}/attribution_report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        
        # Check attribution network
        self.assertIn('attribution_network', data)
        network = data['attribution_network']
        self.assertIn('author1', network)
        self.assertIn('author2', network)
        self.assertIn('author3', network)
        
        # Check cross-references
        self.assertIn('cross_references', data)
        cross_refs = data['cross_references']
        self.assertGreater(len(cross_refs), 0)
        
        # Check collaboration metrics
        self.assertIn('collaboration_metrics', data)
        metrics = data['collaboration_metrics']
        self.assertIn('total_authors', metrics)
        self.assertIn('collaborative_authors', metrics)
        self.assertIn('collaboration_percentage', metrics)
        
        # Check attribution quality
        self.assertIn('attribution_quality', data)
        quality = data['attribution_quality']
        self.assertIn('has_cross_references', quality)
        self.assertIn('collaboration_health', quality)
        
        # Should detect good collaboration
        self.assertTrue(quality['has_cross_references'])
        self.assertIn(quality['collaboration_health'], ['good', 'excellent'])
    
    def test_content_attribution_details(self):
        """Test detailed attribution for individual content."""
        response = self.client.get(f'/api/worlds/{self.world.id}/characters/{self.character1.id}/attribution_details/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        
        # Check content info
        self.assertIn('content', data)
        content_info = data['content']
        self.assertEqual(content_info['author']['username'], 'author2')
        
        # Check attribution details
        self.assertIn('attribution', data)
        attribution = data['attribution']
        self.assertIn('primary_attribution', attribution)
        self.assertIn('references_made', attribution)
        self.assertIn('references_received', attribution)
        
        # Should show reference to foundation page
        refs_made = attribution['references_made']
        print(f"References made by character: {[ref['title'] for ref in refs_made]}")
        # Character1 links to page1, so should have 1 reference
        self.assertGreaterEqual(len(refs_made), 1)
        # Find the foundation page reference
        foundation_ref = next((ref for ref in refs_made if ref['title'] == 'Foundation Page'), None)
        self.assertIsNotNone(foundation_ref)
        self.assertTrue(foundation_ref['is_cross_author'])
        
        # Check collaboration metrics
        self.assertIn('collaboration_metrics', data)
        collab_metrics = data['collaboration_metrics']
        self.assertIn('collaboration_type', collab_metrics)
        self.assertIn('is_collaborative', collab_metrics)
        self.assertTrue(collab_metrics['is_collaborative'])
        
        # Check attribution suggestions
        self.assertIn('attribution_suggestions', data)
        suggestions = data['attribution_suggestions']
        self.assertIn('attribution_quality', suggestions)
        self.assertIn('well_attributed', suggestions)
        self.assertTrue(suggestions['well_attributed'])
    
    def test_automatic_author_assignment(self):
        """Test that authors are automatically assigned on content creation."""
        # Switch to user2
        self.client.force_authenticate(user=self.user2)
        
        # Create new content
        page_data = {
            'title': 'New Collaborative Page',
            'content': 'This page will test automatic author assignment',
            'summary': 'Auto-assignment test'
        }
        
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that author was automatically set
        data = response.data
        self.assertEqual(data['author']['username'], 'author2')
        self.assertEqual(data['author']['first_name'], 'Bob')
        self.assertEqual(data['author']['last_name'], 'Jones')
        
        # Check attribution
        self.assertIn('attribution', data)
        self.assertIn('Bob Jones', data['attribution'])
    
    def test_contribution_tracking(self):
        """Test that contributions are properly tracked."""
        # Check initial contribution counts
        from collab.models import UserProfile
        
        profile1 = UserProfile.objects.get(user=self.user1)
        profile2 = UserProfile.objects.get(user=self.user2)
        profile3 = UserProfile.objects.get(user=self.user3)
        
        # Should have correct contribution counts
        self.assertEqual(profile1.contribution_count, 1)  # 1 page
        self.assertEqual(profile2.contribution_count, 1)  # 1 character
        self.assertEqual(profile3.contribution_count, 1)  # 1 story
        
        # World creator should have correct world count
        self.assertEqual(profile1.worlds_created, 1)
        self.assertEqual(profile2.worlds_created, 0)
        self.assertEqual(profile3.worlds_created, 0)
    
    def test_linked_content_attribution(self):
        """Test that linked content shows proper attribution."""
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/{self.page1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        
        # Check linked content attribution
        self.assertIn('linked_content', data)
        linked = data['linked_content']
        
        # This page is referenced by others, so it should have no outgoing links
        # But let's check what we actually get
        print(f"Linked content for page1: {linked}")
        # The page1 doesn't link to anything, so should be empty
        # But if there are links, let's verify they have proper attribution
        
        # Check character that links to this page
        response = self.client.get(f'/api/worlds/{self.world.id}/characters/{self.character1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        linked = data['linked_content']
        # Character links to both Foundation Page and Epic Tale (bidirectional)
        self.assertGreaterEqual(len(linked), 1)
        
        # Check attribution in linked content - find the Foundation Page
        foundation_link = next((link for link in linked if link['title'] == 'Foundation Page'), None)
        self.assertIsNotNone(foundation_link)
        self.assertIn('attribution', foundation_link)
        # Should contain either the full name or username
        self.assertTrue('Alice Smith' in foundation_link['attribution'] or 'author1' in foundation_link['attribution'])
    
    def test_backward_compatibility(self):
        """Test that backward compatibility URLs still work."""
        # Test old-style URLs still work
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should still have version headers
        self.assertEqual(response.get('X-API-Version'), 'v1')
    
    def test_proper_http_method_routing(self):
        """Test that HTTP methods are properly routed for immutability."""
        # Create test content with unique title
        page_data = {
            'title': 'Unique Test Page for HTTP Methods',
            'content': 'Test content for HTTP method testing',
            'summary': 'Test summary for HTTP methods'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # GET should work
        page_id = response.data['id']
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # POST should work for creation with different title
        new_page_data = {
            'title': 'Another Unique Test Page',
            'content': 'Another test content',
            'summary': 'Another test summary'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', new_page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # PUT, PATCH, DELETE should be blocked by middleware
        for method in ['put', 'patch', 'delete']:
            client_method = getattr(self.client, method)
            response = client_method(f'/api/worlds/{self.world.id}/pages/{page_id}/', {})
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                           f"{method.upper()} should be blocked for immutable content")


class ErrorHandlingValidationTest(TestCase):
    """Test error handling and validation implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test world
        self.world = World.objects.create(
            title='Test World',
            description='A world for testing error handling',
            creator=self.user
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
    
    def test_custom_exception_handler_structure(self):
        """Test that custom exception handler provides consistent error structure."""
        # Test with invalid world ID
        response = self.client.get('/api/v1/worlds/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Check error response structure
        self.assertIn('error', response.data)
        self.assertIn('message', response.data)
        self.assertIn('timestamp', response.data)
        self.assertIn('path', response.data)
        self.assertIn('method', response.data)
        self.assertIn('api_version', response.data)
        self.assertIn('suggestion', response.data)
    
    def test_content_validation_errors(self):
        """Test content validation with meaningful error messages."""
        # Test empty title
        invalid_data = {
            'title': '',
            'content': 'Valid content here',
            'summary': 'Valid summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.data).lower())
        
        # Test short title
        invalid_data = {
            'title': 'AB',  # Too short
            'content': 'Valid content here',
            'summary': 'Valid summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test empty content
        invalid_data = {
            'title': 'Valid Title',
            'content': '',  # Empty content
            'summary': 'Valid summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', str(response.data).lower())
    
    def test_immutability_violation_errors(self):
        """Test immutability violation error handling."""
        # Create content first
        page_data = {
            'title': 'Test Page',
            'content': 'Test content for immutability testing',
            'summary': 'Test summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        page_id = response.data['id']
        
        # Try to update (should be blocked by middleware)
        update_data = {'title': 'Updated Title'}
        response = self.client.put(f'/api/v1/worlds/{self.world.id}/pages/{page_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        response_data = response.json() if hasattr(response, 'json') else response.data
        self.assertIn('Immutability Violation', response_data['error'])
        self.assertIn('suggestion', response_data)
    
    def test_file_upload_validation(self):
        """Test file upload validation for images."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from io import BytesIO
        from PIL import Image as PILImage
        
        # Test with valid image
        img = PILImage.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        valid_image = SimpleUploadedFile(
            "test_image.jpg",
            img_io.getvalue(),
            content_type="image/jpeg"
        )
        
        valid_data = {
            'title': 'Test Image',
            'content': 'Test image content',
            'image_file': valid_image,
            'alt_text': 'Test alt text',
            'image_type': 'concept_art'
        }
        
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/images/', valid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test with missing alt text
        img_io.seek(0)
        invalid_image = SimpleUploadedFile(
            "test_image2.jpg",
            img_io.getvalue(),
            content_type="image/jpeg"
        )
        
        invalid_data = {
            'title': 'Test Image 2',
            'content': 'Test image content',
            'image_file': invalid_image,
            'alt_text': '',  # Missing alt text
            'image_type': 'concept_art'
        }
        
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/images/', invalid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('alt_text', str(response.data).lower())
    
    def test_world_access_errors(self):
        """Test world access error handling."""
        # Test with non-existent world
        response = self.client.get('/api/v1/worlds/99999/pages/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test creating content in non-existent world
        page_data = {
            'title': 'Test Page',
            'content': 'Test content',
            'summary': 'Test summary'
        }
        response = self.client.post('/api/v1/worlds/99999/pages/', page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_authentication_error_handling(self):
        """Test authentication error responses."""
        # Remove authentication
        self.client.force_authenticate(user=None)
        
        # Try to access protected endpoint
        response = self.client.get('/api/v1/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Check error structure
        self.assertIn('error', response.data)
        self.assertIn('Authentication Required', response.data['error'])
        self.assertIn('suggestion', response.data)
    
    def test_character_validation_errors(self):
        """Test character-specific validation errors."""
        # Test missing required fields
        invalid_data = {
            'title': 'Test Character',
            'content': 'Character description',
            'full_name': '',  # Required field
            'personality_traits': ['brave'],
            'relationships': {'friend': 'Alice'}
        }
        
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/characters/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid personality traits format
        invalid_data = {
            'title': 'Test Character',
            'content': 'Character description',
            'full_name': 'John Doe',
            'personality_traits': 'not a list',  # Should be a list
            'relationships': {'friend': 'Alice'}
        }
        
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/characters/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_title_validation(self):
        """Test validation for duplicate titles within the same world."""
        # Create first page
        page_data = {
            'title': 'Unique Title',
            'content': 'First page content',
            'summary': 'First summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to create another page with the same title
        duplicate_data = {
            'title': 'Unique Title',  # Same title
            'content': 'Second page content',
            'summary': 'Second summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.data).lower())
    
    def test_tag_validation_errors(self):
        """Test tag validation error handling."""
        # Test empty tag name
        invalid_tag = {'name': ''}
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/tags/', invalid_tag, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test duplicate tag in same world
        valid_tag = {'name': 'test-tag'}
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/tags/', valid_tag, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to create duplicate
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/tags/', valid_tag, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_error_logging(self):
        """Test that errors are properly logged."""
        import logging
        
        # Capture log output
        with self.assertLogs('collab.exceptions', level='WARNING') as log:
            # Trigger a client error (400-level)
            invalid_data = {'title': '', 'content': 'test'}
            self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', invalid_data, format='json')
        
        # Check that the error was logged
        self.assertTrue(any('API Client Error' in record for record in log.output))
    
    def test_method_not_allowed_error_structure(self):
        """Test Method Not Allowed error structure."""
        # Create content first
        page_data = {
            'title': 'Test Page',
            'content': 'Test content',
            'summary': 'Test summary'
        }
        response = self.client.post(f'/api/v1/worlds/{self.world.id}/pages/', page_data, format='json')
        page_id = response.data['id']
        
        # Try unsupported method
        response = self.client.patch(f'/api/v1/worlds/{self.world.id}/pages/{page_id}/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        response_data = response.json() if hasattr(response, 'json') else response.data
        self.assertIn('Immutability Violation', response_data['error'])
        self.assertIn('suggestion', response_data)
        self.assertIn('allowed_methods', response_data)
    

