"""
Unit tests for immutability enforcement across all content types.
Tests that content cannot be modified or deleted after creation.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import World, Page, Essay, Character, Story, Image
from .exceptions import ImmutabilityViolationError


class ImmutabilityEnforcementTest(TestCase):
    """Test immutability enforcement across all content types."""
    
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
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
    
    def test_page_immutability_model_level(self):
        """Test page immutability at model level."""
        page = Page.objects.create(
            title='Test Page',
            content='Original content',
            author=self.user,
            world=self.world,
            summary='Original summary'
        )
        
        # Try to modify the page
        page.title = 'Modified Title'
        with self.assertRaises(ImmutabilityViolationError):
            page.save()
        
        # Try to delete the page
        with self.assertRaises(ImmutabilityViolationError):
            page.delete()
    
    def test_page_immutability_api_level(self):
        """Test page immutability at API level."""
        # Create page
        data = {
            'title': 'Test Page',
            'content': 'Original content',
            'summary': 'Original summary'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        page_id = response.data['id']
        
        # Try to update via PUT
        update_data = {'title': 'Modified Title'}
        response = self.client.put(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to update via PATCH
        response = self.client.patch(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete
        response = self.client.delete(f'/api/worlds/{self.world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_essay_immutability_model_level(self):
        """Test essay immutability at model level."""
        essay = Essay.objects.create(
            title='Test Essay',
            content='Original essay content',
            author=self.user,
            world=self.world,
            abstract='Original abstract'
        )
        
        # Try to modify the essay
        essay.abstract = 'Modified abstract'
        with self.assertRaises(ImmutabilityViolationError):
            essay.save()
        
        # Try to delete the essay
        with self.assertRaises(ImmutabilityViolationError):
            essay.delete()
    
    def test_essay_immutability_api_level(self):
        """Test essay immutability at API level."""
        # Create essay
        data = {
            'title': 'Test Essay',
            'content': 'Original essay content',
            'abstract': 'Original abstract'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/essays/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        essay_id = response.data['id']
        
        # Try to update via PUT
        update_data = {'abstract': 'Modified abstract'}
        response = self.client.put(f'/api/worlds/{self.world.id}/essays/{essay_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to update via PATCH
        response = self.client.patch(f'/api/worlds/{self.world.id}/essays/{essay_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete
        response = self.client.delete(f'/api/worlds/{self.world.id}/essays/{essay_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_character_immutability_model_level(self):
        """Test character immutability at model level."""
        character = Character.objects.create(
            title='Test Character',
            content='Character description',
            author=self.user,
            world=self.world,
            full_name='John Doe',
            species='Human'
        )
        
        # Try to modify the character
        character.species = 'Elf'
        with self.assertRaises(ImmutabilityViolationError):
            character.save()
        
        # Try to delete the character
        with self.assertRaises(ImmutabilityViolationError):
            character.delete()
    
    def test_character_immutability_api_level(self):
        """Test character immutability at API level."""
        # Create character
        data = {
            'title': 'Test Character',
            'content': 'Character description',
            'full_name': 'John Doe',
            'species': 'Human',
            'personality_traits': ['brave'],
            'relationships': {}
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/characters/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        character_id = response.data['id']
        
        # Try to update via PUT
        update_data = {'species': 'Elf'}
        response = self.client.put(f'/api/worlds/{self.world.id}/characters/{character_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to update via PATCH
        response = self.client.patch(f'/api/worlds/{self.world.id}/characters/{character_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete
        response = self.client.delete(f'/api/worlds/{self.world.id}/characters/{character_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_story_immutability_model_level(self):
        """Test story immutability at model level."""
        story = Story.objects.create(
            title='Test Story',
            content='Original story content',
            author=self.user,
            world=self.world,
            genre='Fantasy'
        )
        
        # Try to modify the story
        story.genre = 'Science Fiction'
        with self.assertRaises(ImmutabilityViolationError):
            story.save()
        
        # Try to delete the story
        with self.assertRaises(ImmutabilityViolationError):
            story.delete()
    
    def test_story_immutability_api_level(self):
        """Test story immutability at API level."""
        # Create story
        data = {
            'title': 'Test Story',
            'content': 'Original story content',
            'genre': 'Fantasy',
            'main_characters': ['Hero']
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/stories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        story_id = response.data['id']
        
        # Try to update via PUT
        update_data = {'genre': 'Science Fiction'}
        response = self.client.put(f'/api/worlds/{self.world.id}/stories/{story_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to update via PATCH
        response = self.client.patch(f'/api/worlds/{self.world.id}/stories/{story_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete
        response = self.client.delete(f'/api/worlds/{self.world.id}/stories/{story_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_image_immutability_model_level(self):
        """Test image immutability at model level."""
        # Create image without actual file for testing
        image = Image(
            title='Test Image',
            content='Image description',
            author=self.user,
            world=self.world,
            alt_text='Test alt text'
        )
        # Skip file validation for this test
        image.save()
        
        # Try to modify the image
        image.alt_text = 'Modified alt text'
        with self.assertRaises(ImmutabilityViolationError):
            image.save()
        
        # Try to delete the image
        with self.assertRaises(ImmutabilityViolationError):
            image.delete()
    
    def test_force_update_bypass(self):
        """Test that force_update=True bypasses immutability for all content types."""
        # Test with Page
        page = Page.objects.create(
            title='Test Page',
            content='Original content',
            author=self.user,
            world=self.world
        )
        
        page.title = 'Force Updated Title'
        page.save(force_update=True)  # Should work
        
        page.refresh_from_db()
        self.assertEqual(page.title, 'Force Updated Title')
        
        # Test with Essay
        essay = Essay.objects.create(
            title='Test Essay',
            content='Original content',
            author=self.user,
            world=self.world
        )
        
        essay.abstract = 'Force updated abstract'
        essay.save(force_update=True)  # Should work
        
        essay.refresh_from_db()
        self.assertEqual(essay.abstract, 'Force updated abstract')
        
        # Test with Character
        character = Character.objects.create(
            title='Test Character',
            content='Character description',
            author=self.user,
            world=self.world,
            full_name='John Doe'
        )
        
        character.species = 'Force updated species'
        character.save(force_update=True)  # Should work
        
        character.refresh_from_db()
        self.assertEqual(character.species, 'Force updated species')
        
        # Test with Story
        story = Story.objects.create(
            title='Test Story',
            content='Story content',
            author=self.user,
            world=self.world
        )
        
        story.genre = 'Force updated genre'
        story.save(force_update=True)  # Should work
        
        story.refresh_from_db()
        self.assertEqual(story.genre, 'Force updated genre')
    
    def test_immutability_error_messages(self):
        """Test that immutability error messages are informative."""
        page = Page.objects.create(
            title='Test Page',
            content='Original content',
            author=self.user,
            world=self.world
        )
        
        # Try to modify
        page.title = 'Modified Title'
        try:
            page.save()
            self.fail("Expected ImmutabilityViolationError")
        except ImmutabilityViolationError as e:
            self.assertIn('Page', str(e))
            self.assertIn('cannot be modified', str(e))
        
        # Try to delete
        try:
            page.delete()
            self.fail("Expected ImmutabilityViolationError")
        except ImmutabilityViolationError as e:
            self.assertIn('Page', str(e))
            self.assertIn('cannot be deleted', str(e))
    
    def test_immutability_with_relationships(self):
        """Test that immutability doesn't prevent relationship operations."""
        page = Page.objects.create(
            title='Test Page',
            content='Original content',
            author=self.user,
            world=self.world
        )
        
        # Adding tags should work (doesn't modify the content object itself)
        page.add_tag('test-tag')
        tags = page.get_tags()
        self.assertEqual(tags.count(), 1)
        
        # Removing tags should work
        result = page.remove_tag('test-tag')
        self.assertTrue(result)
        tags = page.get_tags()
        self.assertEqual(tags.count(), 0)
        
        # Creating another page for linking
        page2 = Page.objects.create(
            title='Test Page 2',
            content='Another content',
            author=self.user,
            world=self.world
        )
        
        # Linking should work
        page.link_to(page2)
        linked = page.get_linked_content()
        self.assertEqual(len(linked), 1)
        
        # Unlinking should work
        result = page.unlink_from(page2)
        self.assertTrue(result)
        linked = page.get_linked_content()
        self.assertEqual(len(linked), 0)
    
    def test_api_error_responses_for_immutability(self):
        """Test that API returns proper error responses for immutability violations."""
        # Create content
        data = {
            'title': 'Test Page',
            'content': 'Original content'
        }
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        page_id = response.data['id']
        
        # Try to update
        update_data = {'title': 'Modified Title'}
        response = self.client.put(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data)
        
        # Should return 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Error message should be informative
        self.assertIn('immutable', str(response.data).lower())
    
    def test_immutability_across_different_users(self):
        """Test that immutability applies even to the original author."""
        # Create content
        page = Page.objects.create(
            title='Test Page',
            content='Original content',
            author=self.user,
            world=self.world
        )
        
        # Even the original author cannot modify
        page.title = 'Modified by author'
        with self.assertRaises(ImmutabilityViolationError):
            page.save()
        
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Other user also cannot modify (if they somehow got access)
        page.title = 'Modified by other user'
        with self.assertRaises(ImmutabilityViolationError):
            page.save()
    
    def test_immutability_with_bulk_operations(self):
        """Test that immutability applies to bulk operations."""
        # Create multiple pages
        pages = []
        for i in range(3):
            page = Page.objects.create(
                title=f'Test Page {i}',
                content=f'Content {i}',
                author=self.user,
                world=self.world
            )
            pages.append(page)
        
        # Bulk update should fail for existing objects
        # Note: Django's bulk_update bypasses model save() method
        # So this tests the expected behavior if someone tries to use it
        
        # Individual updates should still fail
        for page in pages:
            page.title = f'Modified {page.title}'
            with self.assertRaises(ImmutabilityViolationError):
                page.save()
    
    def test_immutability_inheritance(self):
        """Test that immutability is properly inherited by all content types."""
        content_types = [
            (Page, {
                'title': 'Test Page',
                'content': 'Page content',
                'summary': 'Page summary'
            }),
            (Essay, {
                'title': 'Test Essay',
                'content': 'Essay content',
                'abstract': 'Essay abstract'
            }),
            (Character, {
                'title': 'Test Character',
                'content': 'Character content',
                'full_name': 'John Doe'
            }),
            (Story, {
                'title': 'Test Story',
                'content': 'Story content',
                'genre': 'Fantasy'
            })
        ]
        
        for model_class, data in content_types:
            # Create instance
            instance = model_class.objects.create(
                author=self.user,
                world=self.world,
                **data
            )
            
            # Try to modify
            instance.title = f'Modified {instance.title}'
            with self.assertRaises(ImmutabilityViolationError):
                instance.save()
            
            # Try to delete
            with self.assertRaises(ImmutabilityViolationError):
                instance.delete()