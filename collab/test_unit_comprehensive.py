"""
Comprehensive unit tests for the collaborative worldbuilding application.
Focuses on core functionality, validation, and business logic.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from .models import World, Page, Essay, Character, Story, Tag, UserProfile
from .serializers import WorldSerializer, PageSerializer, EssaySerializer
from .exceptions import ImmutabilityViolationError, ContentValidationError


class CoreModelValidationTest(TestCase):
    """Test core model validation and constraints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.world = World.objects.create(
            title='Test World',
            description='A test world for validation testing',
            creator=self.user
        )
    
    def test_world_validation(self):
        """Test world model validation."""
        # Valid world
        world = World(
            title='Valid World',
            description='Valid description',
            creator=self.user
        )
        world.full_clean()  # Should not raise
        
        # Invalid world - empty title
        with self.assertRaises(ValidationError):
            world = World(
                title='',
                description='Valid description',
                creator=self.user
            )
            world.full_clean()
        
        # Invalid world - short title
        with self.assertRaises(ValidationError):
            world = World(
                title='AB',
                description='Valid description',
                creator=self.user
            )
            world.full_clean()
    
    def test_page_validation(self):
        """Test page model validation."""
        # Valid page
        page = Page(
            title='Valid Page Title',
            content='This is valid content that meets the minimum length requirement.',
            author=self.user,
            world=self.world,
            summary='Valid summary'
        )
        page.full_clean()  # Should not raise
        
        # Invalid page - empty title
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='',
                content='Valid content that meets minimum length requirements.',
                author=self.user,
                world=self.world
            )
            page.full_clean()
        
        # Invalid page - short content
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='Valid Title',
                content='Short',
                author=self.user,
                world=self.world
            )
            page.full_clean()
    
    def test_essay_validation(self):
        """Test essay model validation."""
        # Valid essay
        essay = Essay(
            title='Valid Essay Title',
            content='This is valid essay content that meets the minimum length requirement for essays.',
            author=self.user,
            world=self.world,
            abstract='Valid abstract'
        )
        essay.full_clean()  # Should not raise
        
        # Word count should be calculated
        essay.save()
        self.assertGreater(essay.word_count, 0)
    
    def test_character_validation(self):
        """Test character model validation."""
        # Valid character
        character = Character(
            title='Valid Character Title',
            content='This is valid character content that meets minimum length requirements.',
            author=self.user,
            world=self.world,
            full_name='John Doe',
            personality_traits=['brave', 'kind'],
            relationships={'friend': 'Alice'}
        )
        character.full_clean()  # Should not raise
        
        # Invalid character - empty full name
        with self.assertRaises(ValidationError):
            character = Character(
                title='Valid Title',
                content='Valid content that meets minimum length requirements.',
                author=self.user,
                world=self.world,
                full_name=''
            )
            character.full_clean()
    
    def test_story_validation(self):
        """Test story model validation."""
        # Valid story
        story = Story(
            title='Valid Story Title',
            content='This is valid story content that meets the minimum length requirement for stories.',
            author=self.user,
            world=self.world,
            genre='Fantasy',
            main_characters=['Hero', 'Villain']
        )
        story.full_clean()  # Should not raise
        
        # Word count should be calculated
        story.save()
        self.assertGreater(story.word_count, 0)
    
    def test_tag_validation(self):
        """Test tag model validation."""
        # Valid tag
        tag = Tag(
            name='fantasy',
            world=self.world
        )
        tag.full_clean()  # Should not raise
        
        # Tag name normalization
        tag = Tag(
            name='  ADVENTURE  ',
            world=self.world
        )
        tag.full_clean()
        self.assertEqual(tag.name, 'adventure')
        
        # Invalid tag - empty name
        with self.assertRaises(ValidationError):
            tag = Tag(
                name='',
                world=self.world
            )
            tag.full_clean()


class ImmutabilityEnforcementTest(TestCase):
    """Test immutability enforcement across content types."""
    
    def setUp(self):
        """Set up test data."""
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
    
    def test_page_immutability(self):
        """Test that pages are immutable after creation."""
        page = Page.objects.create(
            title='Test Page',
            content='This is test content that meets minimum length requirements.',
            author=self.user,
            world=self.world,
            summary='Test summary'
        )
        
        # Try to modify
        page.title = 'Modified Title'
        with self.assertRaises(ImmutabilityViolationError):
            page.save()
        
        # Try to delete
        with self.assertRaises(ImmutabilityViolationError):
            page.delete()
    
    def test_essay_immutability(self):
        """Test that essays are immutable after creation."""
        essay = Essay.objects.create(
            title='Test Essay',
            content='This is test essay content that meets minimum length requirements for essays.',
            author=self.user,
            world=self.world,
            abstract='Test abstract'
        )
        
        # Try to modify
        essay.abstract = 'Modified abstract'
        with self.assertRaises(ImmutabilityViolationError):
            essay.save()
        
        # Try to delete
        with self.assertRaises(ImmutabilityViolationError):
            essay.delete()
    
    def test_force_update_bypass(self):
        """Test that force_update bypasses immutability."""
        page = Page.objects.create(
            title='Test Page',
            content='This is test content that meets minimum length requirements.',
            author=self.user,
            world=self.world
        )
        
        # Should work with force_update
        page.title = 'Force Updated Title'
        page.save(force_update=True)
        
        page.refresh_from_db()
        self.assertEqual(page.title, 'Force Updated Title')


class APIImmutabilityTest(TestCase):
    """Test immutability enforcement at API level."""
    
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
        self.client.force_authenticate(user=self.user)
    
    def test_page_api_immutability(self):
        """Test page immutability through API."""
        # Create page
        data = {
            'title': 'Test Page',
            'content': 'This is test content that meets minimum length requirements.',
            'summary': 'Test summary'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        page_id = response.data['id']
        
        # Try to update (should be blocked)
        update_data = {'title': 'Modified Title'}
        response = self.client.put(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to patch (should be blocked)
        response = self.client.patch(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete (should be blocked)
        response = self.client.delete(f'/api/worlds/{self.world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_essay_api_immutability(self):
        """Test essay immutability through API."""
        # Create essay
        data = {
            'title': 'Test Essay',
            'content': 'This is test essay content that meets minimum length requirements for essays.',
            'abstract': 'Test abstract'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/essays/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        essay_id = response.data['id']
        
        # Try to update (should be blocked)
        update_data = {'abstract': 'Modified abstract'}
        response = self.client.put(f'/api/worlds/{self.world.id}/essays/{essay_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SerializerValidationTest(TestCase):
    """Test serializer validation and data transformation."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
    
    def test_world_serializer(self):
        """Test WorldSerializer functionality."""
        serializer = WorldSerializer(self.world)
        data = serializer.data
        
        # Check required fields
        self.assertEqual(data['title'], 'Test World')
        self.assertEqual(data['creator']['username'], 'testuser')
        self.assertIn('content_counts', data)
        self.assertIn('contributor_count', data)
        self.assertIn('collaboration_stats', data)
    
    def test_page_serializer(self):
        """Test PageSerializer functionality."""
        page = Page.objects.create(
            title='Test Page',
            content='This is test content that meets minimum length requirements.',
            author=self.user,
            world=self.world,
            summary='Test summary'
        )
        
        serializer = PageSerializer(page)
        data = serializer.data
        
        # Check required fields
        self.assertEqual(data['title'], 'Test Page')
        self.assertEqual(data['author']['username'], 'testuser')
        self.assertIn('attribution', data)
        self.assertIn('collaboration_info', data)
        self.assertIn('tags', data)
        self.assertIn('linked_content', data)
    
    def test_essay_serializer(self):
        """Test EssaySerializer functionality."""
        essay = Essay.objects.create(
            title='Test Essay',
            content='This is test essay content that meets minimum length requirements for essays.',
            author=self.user,
            world=self.world,
            abstract='Test abstract'
        )
        
        serializer = EssaySerializer(essay)
        data = serializer.data
        
        # Check required fields
        self.assertEqual(data['title'], 'Test Essay')
        self.assertEqual(data['abstract'], 'Test abstract')
        self.assertGreater(data['word_count'], 0)
        self.assertIn('attribution', data)
    
    def test_serializer_validation_errors(self):
        """Test serializer validation error handling."""
        # Test page with invalid data
        invalid_data = {
            'title': '',  # Empty title
            'content': 'Valid content that meets minimum requirements.'
        }
        serializer = PageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
        # Test page with short content
        invalid_data = {
            'title': 'Valid Title',
            'content': 'Short'  # Too short
        }
        serializer = PageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)


class AuthenticationPermissionTest(TestCase):
    """Test authentication and permission functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.creator
        )
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        # World list should require authentication
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Content creation should require authentication
        data = {
            'title': 'Test Page',
            'content': 'This is test content that meets minimum requirements.'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access_allowed(self):
        """Test that authenticated users can access endpoints."""
        self.client.force_authenticate(user=self.other_user)
        
        # Should be able to list worlds
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be able to create content
        data = {
            'title': 'Test Page',
            'content': 'This is test content that meets minimum requirements.',
            'summary': 'Test summary'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_world_creator_permissions(self):
        """Test world creator permissions."""
        # Creator should be able to update world
        self.client.force_authenticate(user=self.creator)
        data = {'title': 'Updated World Title'}
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Non-creator should not be able to update world
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Unauthorized Update'}
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_automatic_author_assignment(self):
        """Test that content author is automatically assigned."""
        self.client.force_authenticate(user=self.other_user)
        
        data = {
            'title': 'Test Page',
            'content': 'This is test content that meets minimum requirements.',
            'summary': 'Test summary'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Author should be automatically set to authenticated user
        self.assertEqual(response.data['author']['username'], 'other')


class TaggingLinkingTest(TestCase):
    """Test tagging and linking functionality."""
    
    def setUp(self):
        """Set up test data."""
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
        self.page1 = Page.objects.create(
            title='Test Page 1',
            content='This is test content for page 1 that meets minimum requirements.',
            author=self.user,
            world=self.world
        )
        self.page2 = Page.objects.create(
            title='Test Page 2',
            content='This is test content for page 2 that meets minimum requirements.',
            author=self.user,
            world=self.world
        )
    
    def test_tag_management(self):
        """Test tag management functionality."""
        # Add tag
        content_tag = self.page1.add_tag('fantasy')
        self.assertIsNotNone(content_tag)
        
        # Check tag was added
        tags = self.page1.get_tags()
        self.assertEqual(tags.count(), 1)
        self.assertEqual(tags.first().name, 'fantasy')
        
        # Remove tag
        result = self.page1.remove_tag('fantasy')
        self.assertTrue(result)
        
        # Check tag was removed
        tags = self.page1.get_tags()
        self.assertEqual(tags.count(), 0)
    
    def test_content_linking(self):
        """Test content linking functionality."""
        # Create link
        link = self.page1.link_to(self.page2)
        self.assertIsNotNone(link)
        
        # Check bidirectional linking
        linked_content = self.page1.get_linked_content()
        self.assertEqual(len(linked_content), 1)
        self.assertEqual(linked_content[0], self.page2)
        
        linking_content = self.page2.get_content_linking_to_this()
        self.assertEqual(len(linking_content), 1)
        self.assertEqual(linking_content[0], self.page1)
        
        # Unlink
        result = self.page1.unlink_from(self.page2)
        self.assertTrue(result)
        
        # Check link was removed
        linked_content = self.page1.get_linked_content()
        self.assertEqual(len(linked_content), 0)
    
    def test_cross_world_linking_prevention(self):
        """Test that content from different worlds cannot be linked."""
        # Create another world and content
        other_world = World.objects.create(
            title='Other World',
            description='Another world',
            creator=self.user
        )
        other_page = Page.objects.create(
            title='Other Page',
            content='This is content in another world that meets minimum requirements.',
            author=self.user,
            world=other_world
        )
        
        # Try to link across worlds
        with self.assertRaises(ValidationError):
            self.page1.link_to(other_page)


class ContributionTrackingTest(TestCase):
    """Test contribution tracking and statistics."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user1
        )
    
    def test_contribution_count_tracking(self):
        """Test that contribution counts are tracked correctly."""
        # Get initial profile
        profile1, created = UserProfile.objects.get_or_create(user=self.user1)
        initial_count = profile1.contribution_count
        
        # Create content
        Page.objects.create(
            title='Test Page',
            content='This is test content that meets minimum requirements.',
            author=self.user1,
            world=self.world
        )
        
        # Check contribution count was updated
        profile1.refresh_from_db()
        self.assertEqual(profile1.contribution_count, initial_count + 1)
    
    def test_world_creation_tracking(self):
        """Test that world creation is tracked in user profiles."""
        # Get initial profile
        profile1, created = UserProfile.objects.get_or_create(user=self.user1)
        initial_count = profile1.worlds_created
        
        # Create another world
        World.objects.create(
            title='Another World',
            description='Another test world',
            creator=self.user1
        )
        
        # Check world count was updated
        profile1.refresh_from_db()
        self.assertEqual(profile1.worlds_created, initial_count + 1)
    
    def test_collaboration_statistics(self):
        """Test collaboration statistics calculation."""
        # Create content by different users
        page1 = Page.objects.create(
            title='Page by User 1',
            content='This is content by user 1 that meets minimum requirements.',
            author=self.user1,
            world=self.world
        )
        page2 = Page.objects.create(
            title='Page by User 2',
            content='This is content by user 2 that meets minimum requirements.',
            author=self.user2,
            world=self.world
        )
        
        # Create cross-author link
        page1.link_to(page2)
        
        # Test world serializer includes collaboration stats
        serializer = WorldSerializer(self.world)
        data = serializer.data
        
        self.assertIn('collaboration_stats', data)
        self.assertIn('top_contributors', data)
        
        # Should detect collaboration
        collab_stats = data['collaboration_stats']
        self.assertGreater(collab_stats['cross_author_collaborations'], 0)


class BusinessLogicTest(TestCase):
    """Test business logic and workflows."""
    
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
        self.client.force_authenticate(user=self.user)
    
    def test_content_creation_workflow(self):
        """Test complete content creation workflow."""
        # Create page with tags
        data = {
            'title': 'Test Page',
            'content': 'This is test content that meets minimum requirements.',
            'summary': 'Test summary',
            'tags': ['fantasy', 'adventure']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that author and world are set
        self.assertEqual(response.data['author']['username'], 'testuser')
        self.assertEqual(response.data['world'], self.world.id)
        
        # Check that attribution is included
        self.assertIn('attribution', response.data)
        self.assertIn('Test User', response.data['attribution'])
    
    def test_chronological_ordering(self):
        """Test that content is ordered chronologically."""
        import time
        
        # Create first page
        page1 = Page.objects.create(
            title='First Page',
            content='This is the first page content that meets minimum requirements.',
            author=self.user,
            world=self.world
        )
        
        # Small delay
        time.sleep(0.01)
        
        # Create second page
        page2 = Page.objects.create(
            title='Second Page',
            content='This is the second page content that meets minimum requirements.',
            author=self.user,
            world=self.world
        )
        
        # Get pages (should be ordered newest first)
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        pages = response.data
        if isinstance(pages, dict) and 'results' in pages:
            pages = pages['results']
        
        # Should be ordered by creation date (newest first)
        self.assertTrue(pages[0]['created_at'] >= pages[1]['created_at'])
    
    def test_world_content_isolation(self):
        """Test that content is isolated between worlds."""
        # Create another world
        other_world = World.objects.create(
            title='Other World',
            description='Another world',
            creator=self.user
        )
        
        # Create content in first world
        Page.objects.create(
            title='Page in World 1',
            content='This content is in world 1 and meets minimum requirements.',
            author=self.user,
            world=self.world
        )
        
        # Create content in second world
        Page.objects.create(
            title='Page in World 2',
            content='This content is in world 2 and meets minimum requirements.',
            author=self.user,
            world=other_world
        )
        
        # List pages in first world
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        pages = response.data
        if isinstance(pages, dict) and 'results' in pages:
            pages = pages['results']
        
        # Should only show content from first world
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0]['title'], 'Page in World 1')
    
    def test_attribution_display(self):
        """Test that attribution is properly displayed."""
        page = Page.objects.create(
            title='Test Page',
            content='This is test content that meets minimum requirements.',
            author=self.user,
            world=self.world
        )
        
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/{page.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check attribution
        self.assertIn('attribution', response.data)
        attribution = response.data['attribution']
        self.assertIn('Created by', attribution)
        self.assertIn('testuser', attribution)
        
        # Check collaboration info
        self.assertIn('collaboration_info', response.data)
        collab_info = response.data['collaboration_info']
        self.assertIn('is_collaborative', collab_info)
        self.assertIn('collaboration_score', collab_info)