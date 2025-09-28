"""
Unit tests for serializers in the collaborative worldbuilding application.
Tests serializer validation, data transformation, and business logic.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework import serializers
from .models import World, Page, Essay, Character, Story, Image, Tag, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserSerializer,
    PasswordChangeSerializer, WorldSerializer, TagSerializer,
    ContentBaseSerializer, PageSerializer, EssaySerializer,
    CharacterSerializer, StorySerializer, ImageSerializer
)


class UserRegistrationSerializerTest(TestCase):
    """Test UserRegistrationSerializer validation and functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Test bio',
            'preferred_content_types': ['page', 'character']
        }
    
    def test_valid_registration_data(self):
        """Test serializer with valid registration data."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        
        # Check profile was created
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.preferred_content_types, ['page', 'character'])
    
    def test_username_validation(self):
        """Test username validation rules."""
        # Test short username
        data = self.valid_data.copy()
        data['username'] = 'ab'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        
        # Test invalid characters
        data['username'] = 'test@user'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        
        # Test duplicate username
        User.objects.create_user(username='existing', email='existing@example.com')
        data['username'] = 'existing'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_email_validation(self):
        """Test email validation rules."""
        # Test duplicate email
        User.objects.create_user(
            username='existing', 
            email='existing@example.com'
        )
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_password_confirmation(self):
        """Test password confirmation validation."""
        data = self.valid_data.copy()
        data['password_confirm'] = 'different_password'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)
    
    def test_preferred_content_types_validation(self):
        """Test preferred content types validation."""
        data = self.valid_data.copy()
        data['preferred_content_types'] = ['page', 'invalid_type']
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('preferred_content_types', serializer.errors)


class PasswordChangeSerializerTest(TestCase):
    """Test PasswordChangeSerializer validation and functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        self.factory = APIRequestFactory()
        
    def test_valid_password_change(self):
        """Test serializer with valid password change data."""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        serializer = PasswordChangeSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertTrue(user.check_password('newpassword123'))
    
    def test_incorrect_current_password(self):
        """Test validation with incorrect current password."""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        serializer = PasswordChangeSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('current_password', serializer.errors)
    
    def test_new_password_confirmation(self):
        """Test new password confirmation validation."""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'different_password'
        }
        
        serializer = PasswordChangeSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)


class WorldSerializerTest(TestCase):
    """Test WorldSerializer validation and functionality."""
    
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
    
    def test_world_serialization(self):
        """Test world serialization includes all expected fields."""
        serializer = WorldSerializer(self.world)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test World')
        self.assertEqual(data['description'], 'A test world')
        self.assertEqual(data['creator']['username'], 'testuser')
        self.assertIn('content_counts', data)
        self.assertIn('contributor_count', data)
        self.assertIn('collaboration_stats', data)
        self.assertIn('top_contributors', data)
    
    def test_content_counts_calculation(self):
        """Test content counts are calculated correctly."""
        # Create some content
        Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        Essay.objects.create(
            title='Test Essay',
            content='Test essay content',
            author=self.user,
            world=self.world
        )
        
        serializer = WorldSerializer(self.world)
        content_counts = serializer.data['content_counts']
        
        self.assertEqual(content_counts['pages'], 1)
        self.assertEqual(content_counts['essays'], 1)
        self.assertEqual(content_counts['characters'], 0)
        self.assertEqual(content_counts['stories'], 0)
        self.assertEqual(content_counts['images'], 0)
    
    def test_contributor_count_calculation(self):
        """Test contributor count is calculated correctly."""
        # Create another user and content
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        Page.objects.create(
            title='Page by User 1',
            content='Content by user 1',
            author=self.user,
            world=self.world
        )
        Page.objects.create(
            title='Page by User 2',
            content='Content by user 2',
            author=user2,
            world=self.world
        )
        
        serializer = WorldSerializer(self.world)
        contributor_count = serializer.data['contributor_count']
        
        self.assertEqual(contributor_count, 2)


class TagSerializerTest(TestCase):
    """Test TagSerializer validation and functionality."""
    
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
    
    def test_tag_name_normalization(self):
        """Test that tag names are normalized during validation."""
        data = {'name': '  FANTASY  '}
        serializer = TagSerializer(data=data, context={'world': self.world})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], 'fantasy')
    
    def test_empty_tag_name_validation(self):
        """Test validation for empty tag name."""
        data = {'name': ''}
        serializer = TagSerializer(data=data, context={'world': self.world})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_duplicate_tag_validation(self):
        """Test validation for duplicate tag names within world."""
        # Create existing tag
        Tag.objects.create(name='fantasy', world=self.world)
        
        # Try to create duplicate
        data = {'name': 'fantasy'}
        serializer = TagSerializer(data=data, context={'world': self.world})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class ContentBaseSerializerTest(TestCase):
    """Test ContentBaseSerializer validation and functionality."""
    
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
        self.page = Page.objects.create(
            title='Test Page',
            content='Test content for the page',
            author=self.user,
            world=self.world
        )
    
    def test_content_serialization(self):
        """Test content serialization includes all expected fields."""
        serializer = PageSerializer(self.page)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Page')
        self.assertEqual(data['content'], 'Test content for the page')
        self.assertEqual(data['author']['username'], 'testuser')
        self.assertIn('attribution', data)
        self.assertIn('collaboration_info', data)
        self.assertIn('tags', data)
        self.assertIn('linked_content', data)
    
    def test_attribution_field(self):
        """Test attribution field formatting."""
        serializer = PageSerializer(self.page)
        attribution = serializer.data['attribution']
        
        self.assertIn('Test User', attribution)
        self.assertIn('Created by', attribution)
    
    def test_collaboration_info_field(self):
        """Test collaboration info field calculation."""
        serializer = PageSerializer(self.page)
        collab_info = serializer.data['collaboration_info']
        
        self.assertIn('links_to_count', collab_info)
        self.assertIn('linked_from_count', collab_info)
        self.assertIn('tags_count', collab_info)
        self.assertIn('is_collaborative', collab_info)
        self.assertIn('collaboration_score', collab_info)
    
    def test_title_validation(self):
        """Test title validation rules."""
        # Test empty title
        data = {'title': '', 'content': 'Valid content'}
        serializer = PageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
        # Test short title
        data = {'title': 'AB', 'content': 'Valid content'}
        serializer = PageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
        # Test long title
        data = {'title': 'A' * 301, 'content': 'Valid content'}
        serializer = PageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_content_validation(self):
        """Test content validation rules."""
        # Test empty content
        data = {'title': 'Valid Title', 'content': ''}
        serializer = PageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
        
        # Test short content
        data = {'title': 'Valid Title', 'content': 'Short'}
        serializer = PageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)


class PageSerializerTest(TestCase):
    """Test PageSerializer specific functionality."""
    
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
    
    def test_page_summary_validation(self):
        """Test page summary validation."""
        data = {
            'title': 'Test Page',
            'content': 'Test content for the page',
            'summary': 'A' * 501  # Too long
        }
        serializer = PageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('summary', serializer.errors)
    
    def test_page_summary_optional(self):
        """Test that page summary is optional."""
        data = {
            'title': 'Test Page',
            'content': 'Test content for the page'
        }
        serializer = PageSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class EssaySerializerTest(TestCase):
    """Test EssaySerializer specific functionality."""
    
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
    
    def test_essay_abstract_validation(self):
        """Test essay abstract validation."""
        data = {
            'title': 'Test Essay',
            'content': 'Test content for the essay',
            'abstract': 'A' * 1001  # Too long
        }
        serializer = EssaySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('abstract', serializer.errors)
    
    def test_essay_word_count_readonly(self):
        """Test that word count is read-only."""
        essay = Essay.objects.create(
            title='Test Essay',
            content='This is a test essay with exactly ten words here.',
            author=self.user,
            world=self.world
        )
        
        serializer = EssaySerializer(essay)
        self.assertEqual(serializer.data['word_count'], 10)
        
        # Word count should be in read-only fields
        self.assertIn('word_count', serializer.Meta.read_only_fields)


class CharacterSerializerTest(TestCase):
    """Test CharacterSerializer specific functionality."""
    
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
    
    def test_character_full_name_validation(self):
        """Test character full name validation."""
        data = {
            'title': 'Test Character',
            'content': 'Character description',
            'full_name': ''  # Empty full name
        }
        serializer = CharacterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('full_name', serializer.errors)
    
    def test_personality_traits_validation(self):
        """Test personality traits validation."""
        # Test non-list value
        data = {
            'title': 'Test Character',
            'content': 'Character description',
            'full_name': 'John Doe',
            'personality_traits': 'not a list'
        }
        serializer = CharacterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('personality_traits', serializer.errors)
    
    def test_relationships_validation(self):
        """Test relationships validation."""
        # Test non-dict value
        data = {
            'title': 'Test Character',
            'content': 'Character description',
            'full_name': 'John Doe',
            'relationships': 'not a dict'
        }
        serializer = CharacterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('relationships', serializer.errors)


class StorySerializerTest(TestCase):
    """Test StorySerializer specific functionality."""
    
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
    
    def test_main_characters_validation(self):
        """Test main characters validation."""
        # Test non-list value
        data = {
            'title': 'Test Story',
            'content': 'Story content',
            'main_characters': 'not a list'
        }
        serializer = StorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('main_characters', serializer.errors)
    
    def test_story_word_count_readonly(self):
        """Test that word count is read-only."""
        story = Story.objects.create(
            title='Test Story',
            content='This is a short story with exactly eight words.',
            author=self.user,
            world=self.world
        )
        
        serializer = StorySerializer(story)
        self.assertEqual(serializer.data['word_count'], 8)
        
        # Word count should be in read-only fields
        self.assertIn('word_count', serializer.Meta.read_only_fields)


class ImageSerializerTest(TestCase):
    """Test ImageSerializer specific functionality."""
    
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
    
    def test_alt_text_validation(self):
        """Test alt text validation for accessibility."""
        data = {
            'title': 'Test Image',
            'content': 'Image description',
            'alt_text': ''  # Empty alt text
        }
        serializer = ImageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('alt_text', serializer.errors)
    
    def test_readonly_fields(self):
        """Test that certain fields are read-only."""
        readonly_fields = ImageSerializer.Meta.read_only_fields
        
        self.assertIn('dimensions', readonly_fields)
        self.assertIn('file_size', readonly_fields)
        self.assertIn('image_url', readonly_fields)


class SerializerContextTest(TestCase):
    """Test serializer context handling."""
    
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
        self.factory = APIRequestFactory()
    
    def test_serializer_with_request_context(self):
        """Test serializers work correctly with request context."""
        request = self.factory.get('/')
        request.user = self.user
        
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        
        serializer = PageSerializer(page, context={'request': request})
        data = serializer.data
        
        # Should include all expected fields
        self.assertIn('attribution', data)
        self.assertIn('collaboration_info', data)
        self.assertIn('author', data)
    
    def test_serializer_without_request_context(self):
        """Test serializers work without request context."""
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        
        serializer = PageSerializer(page)
        data = serializer.data
        
        # Should still include all expected fields
        self.assertIn('attribution', data)
        self.assertIn('collaboration_info', data)
        self.assertIn('author', data)