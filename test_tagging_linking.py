#!/usr/bin/env python
"""
Test script for tagging and linking API endpoints.
Tests all the functionality implemented in task 10.
"""
import os
import sys
import django
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'worldbuilding.settings')
django.setup()

from collab.models import World, Page, Essay, Character, Story, Image, Tag, ContentTag, ContentLink


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
            occupation='Adventurer'
        )
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
    
    def test_tag_management_endpoints(self):
        """Test tag CRUD operations."""
        print("Testing tag management endpoints...")
        
        # Test creating tags
        tag_data = {'name': 'fantasy'}
        response = self.client.post(f'/api/worlds/{self.world.id}/tags/', tag_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'fantasy')
        
        tag_id = response.data['id']
        
        # Test listing tags
        response = self.client.get(f'/api/worlds/{self.world.id}/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test retrieving specific tag
        response = self.client.get(f'/api/worlds/{self.world.id}/tags/{tag_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'fantasy')
        
        # Test updating tag
        update_data = {'name': 'high-fantasy'}
        response = self.client.put(f'/api/worlds/{self.world.id}/tags/{tag_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'high-fantasy')
        
        print("✓ Tag management endpoints working")
    
    def test_content_tagging(self):
        """Test adding tags to content."""
        print("Testing content tagging...")
        
        # Create some tags first
        tag1 = Tag.objects.create(name='adventure', world=self.world)
        tag2 = Tag.objects.create(name='magic', world=self.world)
        
        # Test adding tags to page
        tag_data = {'tags': ['adventure', 'magic', 'new-tag']}
        response = self.client.post(
            f'/api/worlds/{self.world.id}/pages/{self.page1.id}/add-tags/',
            tag_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['added_tags']), 3)
        
        # Verify tags were added
        page_tags = self.page1.get_tags()
        tag_names = [tag.name for tag in page_tags]
        self.assertIn('adventure', tag_names)
        self.assertIn('magic', tag_names)
        self.assertIn('new-tag', tag_names)
        
        print("✓ Content tagging working")
    
    def test_content_linking(self):
        """Test linking content entries."""
        print("Testing content linking...")
        
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
        
        print("✓ Content linking working")
    
    def test_tag_based_search(self):
        """Test searching content by tags."""
        print("Testing tag-based search...")
        
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
        self.assertGreater(results['pages'], 0)
        self.assertGreater(results['characters'], 0)
        
        # Test searching specific content type
        response = self.client.get(
            f'/api/worlds/{self.world.id}/pages/search-by-tags/',
            {'tags': 'fantasy', 'match_all': 'false'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        print("✓ Tag-based search working")
    
    def test_popular_tags(self):
        """Test popular tags endpoint."""
        print("Testing popular tags...")
        
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
        
        print("✓ Popular tags working")
    
    def test_content_link_management(self):
        """Test content link management endpoints."""
        print("Testing content link management...")
        
        # Create a link using the API
        from django.contrib.contenttypes.models import ContentType
        
        page_ct = ContentType.objects.get_for_model(Page)
        char_ct = ContentType.objects.get_for_model(Character)
        
        link_data = {
            'from_content_type': page_ct.id,
            'from_object_id': self.page1.id,
            'to_content_type': char_ct.id,
            'to_object_id': self.character.id
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/links/', link_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        link_id = response.data['id']
        
        # Test listing links
        response = self.client.get(f'/api/worlds/{self.world.id}/links/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        # Test getting links for specific content
        response = self.client.get(
            f'/api/worlds/{self.world.id}/links/for-content/',
            {'content_type': 'page', 'content_id': self.page1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['links_to']), 1)
        
        # Test deleting link
        response = self.client.delete(f'/api/worlds/{self.world.id}/links/{link_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        print("✓ Content link management working")
    
    def test_tag_content_filtering(self):
        """Test filtering content by tags."""
        print("Testing tag content filtering...")
        
        # Create and tag content
        tag = Tag.objects.create(name='test-filter', world=self.world)
        self.page1.add_tag('test-filter')
        self.character.add_tag('test-filter')
        
        # Test getting content for a specific tag
        response = self.client.get(f'/api/worlds/{self.world.id}/tags/{tag.id}/content/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        content_by_type = response.data['content_by_type']
        self.assertEqual(len(content_by_type['pages']), 1)
        self.assertEqual(len(content_by_type['characters']), 1)
        self.assertEqual(content_by_type['pages'][0]['id'], self.page1.id)
        self.assertEqual(content_by_type['characters'][0]['id'], self.character.id)
        
        print("✓ Tag content filtering working")
    
    def test_bulk_link_creation(self):
        """Test bulk creation of content links."""
        print("Testing bulk link creation...")
        
        from django.contrib.contenttypes.models import ContentType
        
        page_ct = ContentType.objects.get_for_model(Page)
        char_ct = ContentType.objects.get_for_model(Character)
        
        bulk_data = {
            'links': [
                {
                    'from_content_type': page_ct.id,
                    'from_object_id': self.page1.id,
                    'to_content_type': char_ct.id,
                    'to_object_id': self.character.id
                },
                {
                    'from_content_type': page_ct.id,
                    'from_object_id': self.page1.id,
                    'to_content_type': page_ct.id,
                    'to_object_id': self.page2.id
                }
            ]
        }
        
        response = self.client.post(
            f'/api/worlds/{self.world.id}/links/bulk-create/',
            bulk_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_created'], 2)
        self.assertEqual(response.data['total_errors'], 0)
        
        print("✓ Bulk link creation working")
    
    def run_all_tests(self):
        """Run all tests."""
        print("Starting tagging and linking API tests...\n")
        
        try:
            self.test_tag_management_endpoints()
            self.test_content_tagging()
            self.test_content_linking()
            self.test_tag_based_search()
            self.test_popular_tags()
            self.test_content_link_management()
            self.test_tag_content_filtering()
            self.test_bulk_link_creation()
            
            print("\n✅ All tagging and linking tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    # Run the tests
    test_case = TaggingLinkingAPITest()
    test_case.setUp()
    success = test_case.run_all_tests()
    
    if success:
        print("\n🎉 Task 10 implementation is working correctly!")
        print("\nImplemented endpoints:")
        print("- Tag management: CRUD operations for tags within worlds")
        print("- Content tagging: Add/remove tags from content entries")
        print("- Content linking: Create bidirectional links between content")
        print("- Tag-based search: Search content by single or multiple tags")
        print("- Popular tags: Get most frequently used tags")
        print("- Link management: CRUD operations for content links")
        print("- Bulk operations: Create multiple links at once")
    else:
        print("\n💥 Some tests failed. Check the implementation.")
        sys.exit(1)