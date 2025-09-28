"""
Integration tests for API workflows in the collaborative worldbuilding application.
Tests complete end-to-end workflows including user registration, authentication,
world creation, content addition, tagging, linking, and chronological features.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITransactionTestCase
from rest_framework import status
from django.db import transaction
import json
import time
from datetime import datetime, timedelta

from .models import World, Page, Essay, Character, Story, Tag, UserProfile


class UserRegistrationAuthenticationWorkflowTest(APITransactionTestCase):
    """Test complete user registration and authentication workflow."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
    
    def test_complete_user_registration_and_authentication_flow(self):
        """Test the complete user registration and authentication workflow."""
        # Step 1: User Registration
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User',
            'bio': 'A new worldbuilder',
            'preferred_content_types': ['page', 'character']
        }
        
        response = self.client.post('/api/auth/register/', registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # Verify profile was created
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.bio, 'A new worldbuilder')
        self.assertEqual(profile.preferred_content_types, ['page', 'character'])
        
        # Step 2: User Login
        login_data = {
            'username': 'newuser',
            'password': 'securepass123'
        }
        
        response = self.client.post('/api/auth/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Extract tokens
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        
        # Step 3: Access Protected Endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'newuser')
        
        # Step 4: Token Refresh
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/auth/refresh/', refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        new_access_token = response.data['access']
        self.assertIsNotNone(new_access_token)
        self.assertNotEqual(access_token, new_access_token)
        
        # Step 5: Use New Token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        return user, new_access_token


class WorldCreationContentWorkflowTest(APITransactionTestCase):
    """Test complete world creation and content addition workflow."""
    
    def setUp(self):
        """Set up authenticated user."""
        self.client = APIClient()
        
        # Create and authenticate user
        self.user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123',
            first_name='World',
            last_name='Creator'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_world_creation_and_content_workflow(self):
        """Test the complete world creation and content addition workflow."""
        # Step 1: Create World
        world_data = {
            'title': 'Fantasy Realm',
            'description': 'A magical world full of adventure and wonder',
            'is_public': True
        }
        
        response = self.client.post('/api/worlds/', world_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        world_id = response.data['id']
        self.assertEqual(response.data['title'], 'Fantasy Realm')
        self.assertEqual(response.data['creator']['username'], 'creator')
        self.assertTrue(response.data['is_public'])
        
        # Verify world exists
        world = World.objects.get(id=world_id)
        self.assertEqual(world.title, 'Fantasy Realm')
        self.assertEqual(world.creator, self.user)
        
        # Step 2: Create Page Content
        page_data = {
            'title': 'Magic System Overview',
            'content': 'This world features a complex magic system based on elemental forces. Magic users must understand the fundamental principles of fire, water, earth, and air to harness their power effectively.',
            'summary': 'Overview of the elemental magic system',
            'tags': ['magic', 'elements', 'system']
        }
        
        response = self.client.post(f'/api/worlds/{world_id}/pages/', page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        page_id = response.data['id']
        self.assertEqual(response.data['title'], 'Magic System Overview')
        self.assertEqual(response.data['author']['username'], 'creator')
        self.assertIn('Created by creator', response.data['attribution'])
        
        # Step 3: Create Character Content
        character_data = {
            'title': 'Archmage Eldrin',
            'content': 'Eldrin is the most powerful mage in the realm, having mastered all four elemental schools of magic. He serves as the head of the Mage Council and mentor to young magic users.',
            'full_name': 'Eldrin Stormweaver',
            'species': 'Human',
            'occupation': 'Archmage',
            'personality_traits': ['wise', 'patient', 'powerful', 'protective'],
            'relationships': {
                'mentor': 'Young mages',
                'leader': 'Mage Council',
                'ally': 'Kingdom of Aethermoor'
            },
            'tags': ['magic', 'archmage', 'mentor']
        }
        
        response = self.client.post(f'/api/worlds/{world_id}/characters/', character_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        character_id = response.data['id']
        self.assertEqual(response.data['title'], 'Archmage Eldrin')
        self.assertEqual(response.data['full_name'], 'Eldrin Stormweaver')
        self.assertEqual(response.data['species'], 'Human')
        
        return world_id, page_id, character_id


class TaggingLinkingWorkflowTest(APITransactionTestCase):
    """Test complete tagging and linking functionality end-to-end."""
    
    def setUp(self):
        """Set up authenticated user and world with content."""
        self.client = APIClient()
        
        # Create and authenticate user
        self.user = User.objects.create_user(
            username='tagger',
            email='tagger@example.com',
            password='testpass123',
            first_name='Tag',
            last_name='Master'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create world
        self.world = World.objects.create(
            title='Tagging Test World',
            description='A world for testing tagging and linking',
            creator=self.user
        )
    
    def test_complete_tagging_and_linking_workflow(self):
        """Test the complete tagging and linking workflow."""
        # Step 1: Create multiple content pieces
        page_data = {
            'title': 'Elemental Magic',
            'content': 'Elemental magic is the foundation of all magical arts in this world. It encompasses the four primary elements: fire, water, earth, and air.',
            'summary': 'Foundation of elemental magic',
            'tags': ['magic', 'elements', 'foundation']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        page_id = response.data['id']
        
        character_data = {
            'title': 'Fire Mage Pyra',
            'content': 'Pyra is a specialist in fire magic, known for her incredible control over flames and her fiery temperament.',
            'full_name': 'Pyra Flameheart',
            'species': 'Human',
            'occupation': 'Fire Mage',
            'personality_traits': ['passionate', 'determined', 'hot-tempered'],
            'relationships': {'teacher': 'Fire Academy'},
            'tags': ['magic', 'fire', 'mage']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/characters/', character_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        character_id = response.data['id']
        
        story_data = {
            'title': 'The Great Fire',
            'content': 'A story about Pyra\'s greatest challenge when she had to contain a magical wildfire that threatened to consume the entire forest.',
            'genre': 'Fantasy',
            'main_characters': ['Pyra Flameheart', 'Forest Guardian'],
            'tags': ['magic', 'fire', 'adventure']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/stories/', story_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        story_id = response.data['id']
        
        # Step 2: Test Tag Management
        # Create additional tags
        tag_data = {'name': 'legendary'}
        response = self.client.post(f'/api/worlds/{self.world.id}/tags/', tag_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Add tags to existing content
        add_tags_data = {'tags': ['legendary', 'powerful']}
        response = self.client.post(f'/api/worlds/{self.world.id}/characters/{character_id}/add-tags/', add_tags_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('legendary', response.data['added_tags'])
        self.assertIn('powerful', response.data['added_tags'])
        
        # Step 3: Test Content Linking
        # Link character to page
        link_data = {
            'links': [
                {
                    'content_type': 'page',
                    'content_id': page_id
                }
            ]
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/characters/{character_id}/add-links/', link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['added_links']), 1)
        
        # Link story to character
        link_data = {
            'links': [
                {
                    'content_type': 'character',
                    'content_id': character_id
                }
            ]
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/stories/{story_id}/add-links/', link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify Bidirectional Linking
        # Check that page shows linked character
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        linked_content = response.data['linked_content']
        self.assertEqual(len(linked_content), 1)
        self.assertEqual(linked_content[0]['id'], character_id)
        self.assertEqual(linked_content[0]['type'], 'character')
        
        # Step 5: Test Tag-based Content Discovery
        response = self.client.get(f'/api/worlds/{self.world.id}/tags/magic/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tagged_content = response.data['tagged_content']
        self.assertEqual(len(tagged_content), 3)  # page, character, story
        
        return page_id, character_id, story_id


class ChronologicalOrderingFilteringWorkflowTest(APITransactionTestCase):
    """Test chronological ordering and filtering functionality."""
    
    def setUp(self):
        """Set up authenticated user and world."""
        self.client = APIClient()
        
        # Create users
        self.user1 = User.objects.create_user(
            username='chrono1',
            email='chrono1@example.com',
            password='testpass123',
            first_name='Chrono',
            last_name='User1'
        )
        self.user2 = User.objects.create_user(
            username='chrono2',
            email='chrono2@example.com',
            password='testpass123',
            first_name='Chrono',
            last_name='User2'
        )
        
        # Create world
        self.world = World.objects.create(
            title='Chronological Test World',
            description='A world for testing chronological features',
            creator=self.user1
        )
    
    def test_chronological_ordering_and_filtering_workflow(self):
        """Test the complete chronological ordering and filtering workflow."""
        # Step 1: Create content with different timestamps (simulate time progression)
        self.client.force_authenticate(user=self.user1)
        
        # Create first piece of content
        page1_data = {
            'title': 'The Beginning',
            'content': 'This is the first entry in our world\'s history, marking the dawn of a new age.',
            'summary': 'The first historical entry',
            'tags': ['history', 'beginning']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', page1_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        page1_id = response.data['id']
        page1_created = response.data['created_at']
        
        # Small delay to ensure different timestamps
        time.sleep(0.1)
        
        # Switch to second user
        self.client.force_authenticate(user=self.user2)
        
        # Create second piece of content
        character_data = {
            'title': 'The First Hero',
            'content': 'The first hero to emerge in this new age, destined to shape the world\'s future.',
            'full_name': 'Aiden Lightbringer',
            'species': 'Human',
            'occupation': 'Hero',
            'personality_traits': ['brave', 'noble', 'determined'],
            'relationships': {'destiny': 'Save the world'},
            'tags': ['hero', 'beginning', 'destiny']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/characters/', character_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        character_id = response.data['id']
        character_created = response.data['created_at']
        
        # Small delay
        time.sleep(0.1)
        
        # Back to first user
        self.client.force_authenticate(user=self.user1)
        
        # Create third piece of content
        story_data = {
            'title': 'The Hero\'s Journey',
            'content': 'The epic tale of how Aiden Lightbringer discovered his destiny and began his quest to save the world from the encroaching darkness.',
            'genre': 'Epic Fantasy',
            'main_characters': ['Aiden Lightbringer'],
            'tags': ['hero', 'journey', 'epic']
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/stories/', story_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        story_id = response.data['id']
        story_created = response.data['created_at']
        
        # Step 2: Test Timeline Ordering (newest first)
        response = self.client.get(f'/api/worlds/{self.world.id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 3)
        
        # Verify chronological order (newest first)
        self.assertEqual(timeline[0]['id'], story_id)
        self.assertEqual(timeline[1]['id'], character_id)
        self.assertEqual(timeline[2]['id'], page1_id)
        
        # Step 3: Test Filtering by Content Type
        response = self.client.get(f'/api/worlds/{self.world.id}/timeline/', {'content_type': 'character'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]['content_type'], 'character')
        self.assertEqual(timeline[0]['id'], character_id)
        
        # Step 4: Test Filtering by Author
        response = self.client.get(f'/api/worlds/{self.world.id}/timeline/', {'author': 'chrono1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 2)  # page and story by chrono1
        for item in timeline:
            self.assertEqual(item['author']['username'], 'chrono1')
        
        # Step 5: Test Filtering by Tags
        response = self.client.get(f'/api/worlds/{self.world.id}/timeline/', {'tags': 'hero'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 2)  # character and story with 'hero' tag
        
        # Step 6: Test Search Functionality
        response = self.client.get(f'/api/worlds/{self.world.id}/timeline/', {'search': 'Aiden'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertGreater(len(timeline), 0)
        
        # Verify search results contain the search term
        found_aiden = False
        for item in timeline:
            if 'Aiden' in item['title'] or 'Aiden' in item.get('content', ''):
                found_aiden = True
                break
        self.assertTrue(found_aiden)
        
        return page1_id, character_id, story_id


class ErrorHandlingEdgeCasesWorkflowTest(APITransactionTestCase):
    """Test error handling and edge cases in API workflows."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        
        # Create authenticated user
        self.user = User.objects.create_user(
            username='errortest',
            email='errortest@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create world
        self.world = World.objects.create(
            title='Error Test World',
            description='A world for testing error scenarios',
            creator=self.user
        )
    
    def test_error_handling_and_edge_cases_workflow(self):
        """Test comprehensive error handling and edge cases."""
        # Step 1: Test Validation Errors
        # Try to create content with invalid data
        invalid_page_data = {
            'title': '',  # Empty title should fail
            'content': 'Valid content that meets minimum length requirements.',
            'summary': 'Valid summary'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', invalid_page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', str(response.data).lower())
        
        # Try to create content with short content
        invalid_page_data = {
            'title': 'Valid Title',
            'content': 'Short',  # Too short
            'summary': 'Valid summary'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', invalid_page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', str(response.data).lower())
        
        # Step 2: Test Duplicate Title Validation
        # Create valid content first
        valid_page_data = {
            'title': 'Unique Page Title',
            'content': 'This is valid content that meets all requirements and has sufficient length.',
            'summary': 'A unique page'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', valid_page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to create another page with same title
        duplicate_page_data = {
            'title': 'Unique Page Title',  # Duplicate title
            'content': 'Different content but same title, which should fail validation.',
            'summary': 'Another page'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', duplicate_page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Step 3: Test Immutability Enforcement
        page_id = Page.objects.filter(world=self.world).first().id
        
        # Try to update immutable content (should return 405 Method Not Allowed)
        update_data = {'title': 'Updated Title'}
        response = self.client.put(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        response = self.client.patch(f'/api/worlds/{self.world.id}/pages/{page_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try to delete immutable content
        response = self.client.delete(f'/api/worlds/{self.world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Step 4: Test Authentication Errors
        # Remove authentication
        self.client.force_authenticate(user=None)
        
        # Try to access protected endpoint
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to create content without authentication
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', valid_page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Step 5: Test Permission Errors
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        # Try to update world created by different user
        world_update_data = {'title': 'Unauthorized Update'}
        response = self.client.patch(f'/api/worlds/{self.world.id}/', world_update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Step 6: Test Not Found Errors
        self.client.force_authenticate(user=self.user)
        
        # Try to access non-existent world
        response = self.client.get('/api/worlds/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Try to access non-existent content
        response = self.client.get(f'/api/worlds/{self.world.id}/pages/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Step 7: Test Cross-World Content Access
        # Create another world
        other_world = World.objects.create(
            title='Other World',
            description='Another world',
            creator=self.user
        )
        
        # Try to access content from one world via another world's endpoint
        response = self.client.get(f'/api/worlds/{other_world.id}/pages/{page_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Step 8: Test Invalid Tag Operations
        # Try to create tag with invalid name
        invalid_tag_data = {'name': 'Invalid Tag Name'}  # Spaces not allowed
        response = self.client.post(f'/api/worlds/{self.world.id}/tags/', invalid_tag_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Step 9: Test Invalid Link Operations
        # Try to create self-referential link
        invalid_link_data = {
            'from_content_type': 'page',
            'from_object_id': page_id,
            'to_content_type': 'page',
            'to_object_id': page_id  # Same as from_object_id
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/links/', invalid_link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        return True


class CompleteCollaborativeWorkflowTest(APITransactionTestCase):
    """Test complete collaborative workflow with multiple users."""
    
    def setUp(self):
        """Set up multiple users for collaborative testing."""
        self.client = APIClient()
        
        # Create multiple users
        self.creator = User.objects.create_user(
            username='worldcreator',
            email='creator@example.com',
            password='testpass123',
            first_name='World',
            last_name='Creator'
        )
        
        self.collaborator1 = User.objects.create_user(
            username='collab1',
            email='collab1@example.com',
            password='testpass123',
            first_name='Collaborator',
            last_name='One'
        )
        
        self.collaborator2 = User.objects.create_user(
            username='collab2',
            email='collab2@example.com',
            password='testpass123',
            first_name='Collaborator',
            last_name='Two'
        )
    
    def test_complete_collaborative_workflow(self):
        """Test a complete collaborative worldbuilding workflow."""
        # Step 1: World Creator creates world
        self.client.force_authenticate(user=self.creator)
        
        world_data = {
            'title': 'Collaborative Fantasy World',
            'description': 'A world built by multiple contributors working together',
            'is_public': True
        }
        
        response = self.client.post('/api/worlds/', world_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        world_id = response.data['id']
        
        # Creator adds initial content
        foundation_page_data = {
            'title': 'World Foundation',
            'content': 'This world is built on the principles of magic and technology coexisting in harmony. The foundation of society rests on the balance between these two forces.',
            'summary': 'The foundational principles of our world',
            'tags': ['foundation', 'magic', 'technology']
        }
        
        response = self.client.post(f'/api/worlds/{world_id}/pages/', foundation_page_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        foundation_page_id = response.data['id']
        
        # Step 2: First Collaborator adds content
        self.client.force_authenticate(user=self.collaborator1)
        
        magic_character_data = {
            'title': 'Master Technomancer',
            'content': 'A master of both magical and technological arts, representing the perfect balance that this world strives for.',
            'full_name': 'Zara Gearwright',
            'species': 'Human',
            'occupation': 'Technomancer',
            'personality_traits': ['innovative', 'balanced', 'wise', 'curious'],
            'relationships': {
                'mentor': 'Young technomancers',
                'colleague': 'Magic Council',
                'inventor': 'Magical devices'
            },
            'tags': ['magic', 'technology', 'balance', 'master']
        }
        
        response = self.client.post(f'/api/worlds/{world_id}/characters/', magic_character_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        character_id = response.data['id']
        
        # Link character to foundation page
        link_data = {
            'links': [
                {
                    'content_type': 'page',
                    'content_id': foundation_page_id
                }
            ]
        }
        
        response = self.client.post(f'/api/worlds/{world_id}/characters/{character_id}/add-links/', link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 3: Second Collaborator adds content
        self.client.force_authenticate(user=self.collaborator2)
        
        story_data = {
            'title': 'The Great Convergence',
            'content': 'The story of how magic and technology first came together, told through the eyes of Zara Gearwright as she discovers the ancient principles that would shape the world.',
            'genre': 'Fantasy',
            'main_characters': ['Zara Gearwright', 'Ancient Spirits', 'Tech Innovators'],
            'tags': ['magic', 'technology', 'convergence', 'history']
        }
        
        response = self.client.post(f'/api/worlds/{world_id}/stories/', story_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        story_id = response.data['id']
        
        # Link story to both character and foundation page
        link_data = {
            'links': [
                {
                    'content_type': 'character',
                    'content_id': character_id
                },
                {
                    'content_type': 'page',
                    'content_id': foundation_page_id
                }
            ]
        }
        
        response = self.client.post(f'/api/worlds/{world_id}/stories/{story_id}/add-links/', link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Test Collaboration Statistics
        self.client.force_authenticate(user=self.creator)
        
        # Check world contributors
        response = self.client.get(f'/api/worlds/{world_id}/contributors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        contributors_data = response.data
        self.assertEqual(contributors_data['total_contributors'], 3)
        
        # Verify all users are listed as contributors
        contributor_usernames = [c['user']['username'] for c in contributors_data['contributors']]
        self.assertIn('worldcreator', contributor_usernames)
        self.assertIn('collab1', contributor_usernames)
        self.assertIn('collab2', contributor_usernames)
        
        # Check collaboration metrics
        self.assertIn('collaboration_summary', contributors_data)
        self.assertGreater(contributors_data['collaboration_summary']['total_cross_author_links'], 0)
        
        # Step 5: Test Attribution Report
        response = self.client.get(f'/api/worlds/{world_id}/attribution_report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        attribution_data = response.data
        self.assertIn('attribution_network', attribution_data)
        self.assertIn('collaboration_health', attribution_data)
        
        # Verify collaboration health is positive
        health_score = attribution_data['collaboration_health']['score']
        self.assertGreater(health_score, 0)
        
        # Step 6: Test Content Attribution Details
        response = self.client.get(f'/api/worlds/{world_id}/stories/{story_id}/attribution_details/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        attribution_details = response.data
        self.assertIn('collaboration_metrics', attribution_details)
        
        # Verify cross-author references are detected
        collab_metrics = attribution_details['collaboration_metrics']
        self.assertTrue(collab_metrics['collaboration_assessment']['is_collaborative'])
        self.assertGreater(collab_metrics['collaboration_assessment']['cross_author_references'], 0)
        
        # Step 7: Test Timeline with Multiple Authors
        response = self.client.get(f'/api/worlds/{world_id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        timeline = response.data['timeline']
        self.assertEqual(len(timeline), 3)  # page, character, story
        
        # Verify different authors in timeline
        authors = [item['author']['username'] for item in timeline]
        self.assertEqual(len(set(authors)), 3)  # Three different authors
        
        # Step 8: Test Search Across Collaborative Content
        response = self.client.get(f'/api/worlds/{world_id}/search/', {'q': 'technology'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        search_results = response.data['results']
        self.assertGreater(len(search_results), 0)
        
        # Verify search finds content from multiple authors
        search_authors = [result['author']['username'] for result in search_results]
        self.assertGreater(len(set(search_authors)), 1)
        
        return world_id, foundation_page_id, character_id, story_id