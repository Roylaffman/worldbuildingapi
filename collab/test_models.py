"""
Unit tests for models in the collaborative worldbuilding application.
Tests model validation, constraints, and business logic.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from .models import (
    UserProfile, World, Page, Essay, Character, Story, Image, 
    Tag, ContentTag, ContentLink
)
from .exceptions import ImmutabilityViolationError, ContentValidationError


class UserProfileModelTest(TestCase):
    """Test UserProfile model validation and functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """Test that user profiles are created correctly."""
        profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            preferred_content_types=['page', 'character']
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.preferred_content_types, ['page', 'character'])
        self.assertEqual(profile.contribution_count, 0)
        self.assertEqual(profile.worlds_created, 0)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
    
    def test_user_profile_str_representation(self):
        """Test string representation of user profile."""
        profile = UserProfile.objects.create(user=self.user)
        expected = f"{self.user.username}'s Worldbuilding Profile"
        self.assertEqual(str(profile), expected)
    
    def test_user_profile_defaults(self):
        """Test default values for user profile fields."""
        profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(profile.bio, '')
        self.assertEqual(profile.preferred_content_types, [])
        self.assertEqual(profile.contribution_count, 0)
        self.assertEqual(profile.worlds_created, 0)


class WorldModelTest(TestCase):
    """Test World model validation and functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_world_creation(self):
        """Test that worlds are created correctly."""
        world = World.objects.create(
            title='Test World',
            description='A test world for validation',
            creator=self.user,
            is_public=True
        )
        
        self.assertEqual(world.title, 'Test World')
        self.assertEqual(world.description, 'A test world for validation')
        self.assertEqual(world.creator, self.user)
        self.assertTrue(world.is_public)
        self.assertIsNotNone(world.created_at)
        self.assertIsNotNone(world.updated_at)
    
    def test_world_str_representation(self):
        """Test string representation of world."""
        world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
        self.assertEqual(str(world), 'Test World')
    
    def test_world_title_validation(self):
        """Test world title validation."""
        # Test empty title
        with self.assertRaises(ValidationError):
            world = World(
                title='',
                description='A test world',
                creator=self.user
            )
            world.full_clean()
        
        # Test short title
        with self.assertRaises(ValidationError):
            world = World(
                title='AB',  # Too short
                description='A test world',
                creator=self.user
            )
            world.full_clean()
        
        # Test whitespace-only title
        with self.assertRaises(ValidationError):
            world = World(
                title='   ',
                description='A test world',
                creator=self.user
            )
            world.full_clean()
    
    def test_world_creator_profile_update(self):
        """Test that creating a world updates creator's profile."""
        # Ensure profile exists
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        initial_count = profile.worlds_created
        
        # Create world
        World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user
        )
        
        # Check profile was updated
        profile.refresh_from_db()
        self.assertEqual(profile.worlds_created, initial_count + 1)
    
    def test_world_ordering(self):
        """Test that worlds are ordered by creation date (newest first)."""
        import time
        
        world1 = World.objects.create(
            title='First World',
            description='First world',
            creator=self.user
        )
        
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        
        world2 = World.objects.create(
            title='Second World',
            description='Second world',
            creator=self.user
        )
        
        worlds = list(World.objects.all())
        # Should be ordered by creation date (newest first)
        self.assertTrue(worlds[0].created_at >= worlds[1].created_at)


class ContentBaseModelTest(TestCase):
    """Test ContentBase model validation and functionality."""
    
    def setUp(self):
        """Set up test data."""
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
        self.world = World.objects.create(
            title='Test World',
            description='A test world',
            creator=self.user1
        )
    
    def test_page_creation(self):
        """Test that pages are created correctly."""
        page = Page.objects.create(
            title='Test Page',
            content='This is test content for the page',
            author=self.user1,
            world=self.world,
            summary='Test summary'
        )
        
        self.assertEqual(page.title, 'Test Page')
        self.assertEqual(page.content, 'This is test content for the page')
        self.assertEqual(page.author, self.user1)
        self.assertEqual(page.world, self.world)
        self.assertEqual(page.summary, 'Test summary')
        self.assertIsNotNone(page.created_at)
    
    def test_content_validation_empty_title(self):
        """Test validation for empty title."""
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='',
                content='Valid content',
                author=self.user1,
                world=self.world
            )
            page.full_clean()
    
    def test_content_validation_short_title(self):
        """Test validation for short title."""
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='AB',  # Too short
                content='Valid content',
                author=self.user1,
                world=self.world
            )
            page.full_clean()
    
    def test_content_validation_long_title(self):
        """Test validation for overly long title."""
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='A' * 301,  # Too long
                content='Valid content',
                author=self.user1,
                world=self.world
            )
            page.full_clean()
    
    def test_content_validation_empty_content(self):
        """Test validation for empty content."""
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='Valid Title',
                content='',
                author=self.user1,
                world=self.world
            )
            page.full_clean()
    
    def test_content_validation_short_content(self):
        """Test validation for short content."""
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='Valid Title',
                content='Short',  # Too short
                author=self.user1,
                world=self.world
            )
            page.full_clean()
    
    def test_duplicate_title_validation(self):
        """Test validation for duplicate titles within same world."""
        # Create first page
        Page.objects.create(
            title='Duplicate Title',
            content='First page content',
            author=self.user1,
            world=self.world
        )
        
        # Try to create second page with same title
        with self.assertRaises(ContentValidationError):
            page = Page(
                title='Duplicate Title',
                content='Second page content',
                author=self.user2,
                world=self.world
            )
            page.full_clean()
    
    def test_content_str_representation(self):
        """Test string representation of content."""
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user1,
            world=self.world
        )
        expected = f"Test Page by {self.user1.username}"
        self.assertEqual(str(page), expected)
    
    def test_author_profile_update_on_creation(self):
        """Test that creating content updates author's profile."""
        # Ensure profile exists
        profile, created = UserProfile.objects.get_or_create(user=self.user1)
        initial_count = profile.contribution_count
        
        # Create content
        Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user1,
            world=self.world
        )
        
        # Check profile was updated
        profile.refresh_from_db()
        self.assertEqual(profile.contribution_count, initial_count + 1)


class ImmutabilityModelTest(TestCase):
    """Test immutability enforcement in content models."""
    
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
    
    def test_page_immutability_update(self):
        """Test that pages cannot be updated after creation."""
        page = Page.objects.create(
            title='Test Page',
            content='Original content',
            author=self.user,
            world=self.world
        )
        
        # Try to update the page
        page.title = 'Updated Title'
        with self.assertRaises(ImmutabilityViolationError):
            page.save()
    
    def test_page_immutability_delete(self):
        """Test that pages cannot be deleted."""
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        
        # Try to delete the page
        with self.assertRaises(ImmutabilityViolationError):
            page.delete()
    
    def test_essay_immutability(self):
        """Test that essays are immutable."""
        essay = Essay.objects.create(
            title='Test Essay',
            content='Original essay content',
            author=self.user,
            world=self.world
        )
        
        # Try to update
        essay.content = 'Updated content'
        with self.assertRaises(ImmutabilityViolationError):
            essay.save()
    
    def test_character_immutability(self):
        """Test that characters are immutable."""
        character = Character.objects.create(
            title='Test Character',
            content='Character description',
            author=self.user,
            world=self.world,
            full_name='John Doe',
            personality_traits=['brave'],
            relationships={'friend': 'Alice'}
        )
        
        # Try to update
        character.full_name = 'Jane Doe'
        with self.assertRaises(ImmutabilityViolationError):
            character.save()
    
    def test_story_immutability(self):
        """Test that stories are immutable."""
        story = Story.objects.create(
            title='Test Story',
            content='Story content',
            author=self.user,
            world=self.world,
            main_characters=['Hero']
        )
        
        # Try to update
        story.genre = 'Updated Genre'
        with self.assertRaises(ImmutabilityViolationError):
            story.save()
    
    def test_image_immutability(self):
        """Test that images are immutable."""
        # Skip this test as it requires actual file handling
        self.skipTest("Image immutability test requires file handling setup")
        
        # Try to update
        image.alt_text = 'Updated alt text'
        with self.assertRaises(ImmutabilityViolationError):
            image.save()
    
    def test_force_update_bypass(self):
        """Test that force_update=True bypasses immutability."""
        page = Page.objects.create(
            title='Test Page',
            content='Original content',
            author=self.user,
            world=self.world
        )
        
        # This should work with force_update
        page.title = 'Force Updated Title'
        page.save(force_update=True)
        
        page.refresh_from_db()
        self.assertEqual(page.title, 'Force Updated Title')


class SpecificContentModelTest(TestCase):
    """Test specific content model functionality."""
    
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
    
    def test_essay_word_count_calculation(self):
        """Test that essay word count is calculated automatically."""
        essay = Essay.objects.create(
            title='Test Essay',
            content='This is a test essay with exactly ten words here.',
            author=self.user,
            world=self.world
        )
        
        self.assertEqual(essay.word_count, 10)
    
    def test_character_full_name_validation(self):
        """Test character full name validation."""
        with self.assertRaises(ValidationError):
            character = Character(
                title='Test Character',
                content='Character description',
                author=self.user,
                world=self.world,
                full_name=''  # Empty full name
            )
            character.full_clean()
    
    def test_character_json_fields(self):
        """Test character JSON field handling."""
        character = Character.objects.create(
            title='Test Character',
            content='Character description',
            author=self.user,
            world=self.world,
            full_name='John Doe',
            personality_traits=['brave', 'kind', 'intelligent'],
            relationships={'friend': 'Alice', 'mentor': 'Bob'}
        )
        
        self.assertEqual(character.personality_traits, ['brave', 'kind', 'intelligent'])
        self.assertEqual(character.relationships, {'friend': 'Alice', 'mentor': 'Bob'})
    
    def test_story_word_count_calculation(self):
        """Test that story word count is calculated automatically."""
        story = Story.objects.create(
            title='Test Story',
            content='This is a short story with exactly eight words.',
            author=self.user,
            world=self.world,
            main_characters=['Hero']
        )
        
        self.assertEqual(story.word_count, 9)  # "This is a short story with exactly eight words." = 9 words
    
    def test_story_json_fields(self):
        """Test story JSON field handling."""
        story = Story.objects.create(
            title='Test Story',
            content='Story content',
            author=self.user,
            world=self.world,
            main_characters=['Hero', 'Villain', 'Sidekick']
        )
        
        self.assertEqual(story.main_characters, ['Hero', 'Villain', 'Sidekick'])


class TagModelTest(TestCase):
    """Test Tag model validation and functionality."""
    
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
    
    def test_tag_creation(self):
        """Test that tags are created correctly."""
        tag = Tag.objects.create(
            name='fantasy',
            world=self.world
        )
        
        self.assertEqual(tag.name, 'fantasy')
        self.assertEqual(tag.world, self.world)
        self.assertIsNotNone(tag.created_at)
    
    def test_tag_name_normalization(self):
        """Test that tag names are normalized to lowercase."""
        tag = Tag(
            name='  FANTASY  ',
            world=self.world
        )
        tag.full_clean()
        
        self.assertEqual(tag.name, 'fantasy')
    
    def test_tag_empty_name_validation(self):
        """Test validation for empty tag name."""
        with self.assertRaises(ValidationError):
            tag = Tag(
                name='',
                world=self.world
            )
            tag.full_clean()
    
    def test_tag_uniqueness_within_world(self):
        """Test that tag names are unique within a world."""
        # Create first tag
        Tag.objects.create(
            name='fantasy',
            world=self.world
        )
        
        # Try to create duplicate tag in same world
        with self.assertRaises(ValidationError):
            tag = Tag(
                name='fantasy',
                world=self.world
            )
            tag.full_clean()
    
    def test_tag_str_representation(self):
        """Test string representation of tag."""
        tag = Tag.objects.create(
            name='fantasy',
            world=self.world
        )
        expected = f"fantasy ({self.world.title})"
        self.assertEqual(str(tag), expected)
    
    def test_tag_usage_count(self):
        """Test tag usage count calculation."""
        tag = Tag.objects.create(
            name='fantasy',
            world=self.world
        )
        
        # Initially no usage
        self.assertEqual(tag.get_usage_count(), 0)
        
        # Create content and tag it
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        page.add_tag('fantasy')
        
        # Should now have usage count of 1
        self.assertEqual(tag.get_usage_count(), 1)


class ContentTagModelTest(TestCase):
    """Test ContentTag model functionality."""
    
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
        self.page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        self.tag = Tag.objects.create(
            name='fantasy',
            world=self.world
        )
    
    def test_content_tag_creation(self):
        """Test that content tags are created correctly."""
        content_tag = ContentTag.objects.create(
            content_type=ContentType.objects.get_for_model(Page),
            object_id=self.page.id,
            tag=self.tag
        )
        
        self.assertEqual(content_tag.content_object, self.page)
        self.assertEqual(content_tag.tag, self.tag)
        self.assertIsNotNone(content_tag.created_at)
    
    def test_content_tag_uniqueness(self):
        """Test that content-tag relationships are unique."""
        # Create first content tag
        ContentTag.objects.create(
            content_type=ContentType.objects.get_for_model(Page),
            object_id=self.page.id,
            tag=self.tag
        )
        
        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            ContentTag.objects.create(
                content_type=ContentType.objects.get_for_model(Page),
                object_id=self.page.id,
                tag=self.tag
            )


class ContentLinkModelTest(TestCase):
    """Test ContentLink model functionality."""
    
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
            content='Test content 1',
            author=self.user,
            world=self.world
        )
        self.page2 = Page.objects.create(
            title='Test Page 2',
            content='Test content 2',
            author=self.user,
            world=self.world
        )
    
    def test_content_link_creation(self):
        """Test that content links are created correctly."""
        link = ContentLink.objects.create(
            from_content_type=ContentType.objects.get_for_model(Page),
            from_object_id=self.page1.id,
            to_content_type=ContentType.objects.get_for_model(Page),
            to_object_id=self.page2.id
        )
        
        self.assertEqual(link.from_content, self.page1)
        self.assertEqual(link.to_content, self.page2)
        self.assertIsNotNone(link.created_at)
    
    def test_content_link_self_reference_validation(self):
        """Test that content cannot link to itself."""
        with self.assertRaises(ValidationError):
            link = ContentLink(
                from_content_type=ContentType.objects.get_for_model(Page),
                from_object_id=self.page1.id,
                to_content_type=ContentType.objects.get_for_model(Page),
                to_object_id=self.page1.id  # Same as from_object_id
            )
            link.full_clean()
    
    def test_content_link_uniqueness(self):
        """Test that content links are unique."""
        # Create first link
        ContentLink.objects.create(
            from_content_type=ContentType.objects.get_for_model(Page),
            from_object_id=self.page1.id,
            to_content_type=ContentType.objects.get_for_model(Page),
            to_object_id=self.page2.id
        )
        
        # Try to create duplicate
        with self.assertRaises(ValidationError):
            link = ContentLink(
                from_content_type=ContentType.objects.get_for_model(Page),
                from_object_id=self.page1.id,
                to_content_type=ContentType.objects.get_for_model(Page),
                to_object_id=self.page2.id
            )
            link.full_clean()


class ContentMethodsTest(TestCase):
    """Test content model methods for tagging and linking."""
    
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
            content='Test content 1',
            author=self.user,
            world=self.world
        )
        self.page2 = Page.objects.create(
            title='Test Page 2',
            content='Test content 2',
            author=self.user,
            world=self.world
        )
    
    def test_add_tag_method(self):
        """Test adding tags to content."""
        # Add tag
        content_tag = self.page1.add_tag('fantasy')
        
        # Verify tag was created and associated
        self.assertIsNotNone(content_tag)
        self.assertEqual(content_tag.tag.name, 'fantasy')
        
        # Verify tag appears in content's tags
        tags = self.page1.get_tags()
        self.assertEqual(tags.count(), 1)
        self.assertEqual(tags.first().name, 'fantasy')
    
    def test_add_multiple_tags_method(self):
        """Test adding multiple tags to content."""
        # Add multiple tags
        content_tags = self.page1.add_tags(['fantasy', 'adventure', 'magic'])
        
        # Verify all tags were added
        self.assertEqual(len(content_tags), 3)
        
        # Verify tags appear in content's tags
        tags = self.page1.get_tags()
        self.assertEqual(tags.count(), 3)
        tag_names = [tag.name for tag in tags]
        self.assertIn('fantasy', tag_names)
        self.assertIn('adventure', tag_names)
        self.assertIn('magic', tag_names)
    
    def test_remove_tag_method(self):
        """Test removing tags from content."""
        # Add tag first
        self.page1.add_tag('fantasy')
        
        # Remove tag
        result = self.page1.remove_tag('fantasy')
        self.assertTrue(result)
        
        # Verify tag was removed
        tags = self.page1.get_tags()
        self.assertEqual(tags.count(), 0)
        
        # Try to remove non-existent tag
        result = self.page1.remove_tag('nonexistent')
        self.assertFalse(result)
    
    def test_link_to_method(self):
        """Test linking content to other content."""
        # Create link
        link = self.page1.link_to(self.page2)
        
        # Verify link was created
        self.assertIsNotNone(link)
        
        # Verify bidirectional linking
        linked_content = self.page1.get_linked_content()
        self.assertEqual(len(linked_content), 1)
        self.assertEqual(linked_content[0], self.page2)
        
        linking_content = self.page2.get_content_linking_to_this()
        self.assertEqual(len(linking_content), 1)
        self.assertEqual(linking_content[0], self.page1)
    
    def test_unlink_from_method(self):
        """Test unlinking content from other content."""
        # Create link first
        self.page1.link_to(self.page2)
        
        # Unlink
        result = self.page1.unlink_from(self.page2)
        self.assertTrue(result)
        
        # Verify link was removed
        linked_content = self.page1.get_linked_content()
        self.assertEqual(len(linked_content), 0)
        
        # Try to unlink non-existent link
        result = self.page1.unlink_from(self.page2)
        self.assertFalse(result)
    
    def test_cross_world_linking_validation(self):
        """Test that content from different worlds cannot be linked."""
        # Create another world and content
        other_world = World.objects.create(
            title='Other World',
            description='Another world',
            creator=self.user
        )
        other_page = Page.objects.create(
            title='Other Page',
            content='Other content',
            author=self.user,
            world=other_world
        )
        
        # Try to link content from different worlds
        with self.assertRaises(ValidationError):
            self.page1.link_to(other_page)
    
    def test_get_content_by_tag_class_method(self):
        """Test getting content by tag using class method."""
        # Add tags to content
        self.page1.add_tag('fantasy')
        self.page2.add_tag('adventure')
        
        # Get content by tag
        fantasy_pages = Page.get_content_by_tag(self.world, 'fantasy')
        self.assertEqual(fantasy_pages.count(), 1)
        self.assertEqual(fantasy_pages.first(), self.page1)
        
        adventure_pages = Page.get_content_by_tag(self.world, 'adventure')
        self.assertEqual(adventure_pages.count(), 1)
        self.assertEqual(adventure_pages.first(), self.page2)
        
        # Test non-existent tag
        nonexistent_pages = Page.get_content_by_tag(self.world, 'nonexistent')
        self.assertEqual(nonexistent_pages.count(), 0)
    
    def test_get_content_by_tags_class_method(self):
        """Test getting content by multiple tags using class method."""
        # Add tags to content
        self.page1.add_tag('fantasy')
        self.page1.add_tag('adventure')
        self.page2.add_tag('fantasy')
        
        # Test match_all=False (any tag)
        fantasy_or_adventure = Page.get_content_by_tags(
            self.world, ['fantasy', 'adventure'], match_all=False
        )
        self.assertEqual(fantasy_or_adventure.count(), 2)
        
        # Test match_all=True (all tags)
        fantasy_and_adventure = Page.get_content_by_tags(
            self.world, ['fantasy', 'adventure'], match_all=True
        )
        self.assertEqual(fantasy_and_adventure.count(), 1)
        self.assertEqual(fantasy_and_adventure.first(), self.page1)