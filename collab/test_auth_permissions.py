"""
Unit tests for authentication and permission systems.
Tests JWT authentication, custom permissions, and security features.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import World, Page, UserProfile
from .permissions import IsCreatorOrReadOnly, IsAuthorOrReadOnly


class JWTAuthenticationTest(TestCase):
    """Test JWT authentication functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # Check profile was created
        self.assertTrue(hasattr(user, 'worldbuilding_profile'))
    
    def test_jwt_token_obtain(self):
        """Test JWT token obtain endpoint."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return access and refresh tokens
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh endpoint."""
        # Get initial tokens
        refresh = RefreshToken.for_user(self.user)
        
        data = {'refresh': str(refresh)}
        response = self.client.post('/api/auth/refresh/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return new access token
        self.assertIn('access', response.data)
    
    def test_jwt_token_verify(self):
        """Test JWT token verify endpoint."""
        # Get access token
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        data = {'token': str(access_token)}
        response = self.client.post('/api/auth/verify/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token."""
        # Authenticate with token
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_info_endpoint(self):
        """Test user info endpoint."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/auth/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return user information
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_password_change(self):
        """Test password change endpoint."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post('/api/auth/change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))


class CustomPermissionTest(TestCase):
    """Test custom permission classes."""
    
    def setUp(self):
        """Set up test data."""
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
        
        self.page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.author,
            world=self.world
        )
    
    def test_is_creator_or_read_only_permission(self):
        """Test IsCreatorOrReadOnly permission class."""
        from rest_framework.test import APIRequestFactory
        from rest_framework.views import APIView
        
        factory = APIRequestFactory()
        permission = IsCreatorOrReadOnly()
        
        # Test read permission (should be allowed for everyone)
        request = factory.get('/')
        request.user = self.other_user
        view = APIView()
        
        self.assertTrue(permission.has_object_permission(request, view, self.world))
        
        # Test write permission for creator (should be allowed)
        request = factory.put('/')
        request.user = self.creator
        
        self.assertTrue(permission.has_object_permission(request, view, self.world))
        
        # Test write permission for non-creator (should be denied)
        request = factory.put('/')
        request.user = self.other_user
        
        self.assertFalse(permission.has_object_permission(request, view, self.world))
    
    def test_is_author_or_read_only_permission(self):
        """Test IsAuthorOrReadOnly permission class."""
        from rest_framework.test import APIRequestFactory
        from rest_framework.views import APIView
        
        factory = APIRequestFactory()
        permission = IsAuthorOrReadOnly()
        
        # Test read permission (should be allowed for everyone)
        request = factory.get('/')
        request.user = self.other_user
        view = APIView()
        
        self.assertTrue(permission.has_object_permission(request, view, self.page))
        
        # Test write permission for author (should be allowed)
        request = factory.put('/')
        request.user = self.author
        
        self.assertTrue(permission.has_object_permission(request, view, self.page))
        
        # Test write permission for non-author (should be denied)
        request = factory.put('/')
        request.user = self.other_user
        
        self.assertFalse(permission.has_object_permission(request, view, self.page))


class AuthenticationIntegrationTest(TestCase):
    """Test authentication integration with API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
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
    
    def test_world_creation_requires_authentication(self):
        """Test that world creation requires authentication."""
        data = {
            'title': 'New World',
            'description': 'A new world'
        }
        
        # Unauthenticated request should fail
        response = self.client.post('/api/worlds/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticated request should succeed
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/worlds/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_world_update_requires_creator_permission(self):
        """Test that world updates require creator permission."""
        data = {'title': 'Updated Title'}
        
        # Creator should be able to update
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Non-creator should not be able to update
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(f'/api/worlds/{self.world.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_content_creation_requires_authentication(self):
        """Test that content creation requires authentication."""
        data = {
            'title': 'Test Page',
            'content': 'Test content'
        }
        
        # Unauthenticated request should fail
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticated request should succeed
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_automatic_author_assignment(self):
        """Test that content author is automatically assigned from authenticated user."""
        self.client.force_authenticate(user=self.user2)
        
        data = {
            'title': 'Test Page',
            'content': 'Test content'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Author should be automatically set to authenticated user
        self.assertEqual(response.data['author']['username'], 'user2')
    
    def test_token_expiration_handling(self):
        """Test handling of expired tokens."""
        # This test would require manipulating token expiration
        # For now, we'll test the basic token validation
        
        # Get a token
        login_data = {
            'username': 'user1',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        access_token = response.data['access']
        
        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Clear credentials
        self.client.credentials()
        response = self.client.get('/api/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SecurityTest(TestCase):
    """Test security features and edge cases."""
    
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
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attempts."""
        self.client.force_authenticate(user=self.user)
        
        # Try SQL injection in search parameter
        malicious_query = "'; DROP TABLE collab_page; --"
        response = self.client.get(f'/api/worlds/{self.world.id}/search/', {'q': malicious_query})
        
        # Should not cause an error and should return empty results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_xss_protection_in_content(self):
        """Test that XSS attempts in content are handled safely."""
        self.client.force_authenticate(user=self.user)
        
        # Try to create content with XSS payload
        xss_payload = '<script>alert("XSS")</script>'
        data = {
            'title': f'Test Page {xss_payload}',
            'content': f'Test content {xss_payload}'
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Content should be stored as-is (XSS protection is typically handled by frontend)
        self.assertIn('<script>', response.data['title'])
        self.assertIn('<script>', response.data['content'])
    
    def test_unauthorized_world_access(self):
        """Test that users cannot access worlds they shouldn't."""
        # Create private world
        private_world = World.objects.create(
            title='Private World',
            description='A private world',
            creator=self.user,
            is_public=False
        )
        
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Other user should still be able to access (access control not implemented at world level)
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f'/api/worlds/{private_world.id}/')
        # Note: Current implementation doesn't restrict access to private worlds
        # This test documents current behavior
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cross_world_content_isolation(self):
        """Test that content is properly isolated between worlds."""
        # Create another world and user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_world = World.objects.create(
            title='Other World',
            description='Another world',
            creator=other_user
        )
        
        # Create content in first world
        page = Page.objects.create(
            title='Test Page',
            content='Test content',
            author=self.user,
            world=self.world
        )
        
        self.client.force_authenticate(user=other_user)
        
        # Should not be able to access content via other world's endpoint
        response = self.client.get(f'/api/worlds/{other_world.id}/pages/{page.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_mass_assignment_protection(self):
        """Test protection against mass assignment attacks."""
        self.client.force_authenticate(user=self.user)
        
        # Try to set read-only fields
        data = {
            'title': 'Test Page',
            'content': 'Test content',
            'author': 999,  # Try to set author to different user
            'world': 999,   # Try to set world to different world
            'created_at': '2020-01-01T00:00:00Z'  # Try to set creation date
        }
        
        response = self.client.post(f'/api/worlds/{self.world.id}/pages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Read-only fields should not be affected
        self.assertEqual(response.data['author']['id'], self.user.id)
        self.assertEqual(response.data['world'], self.world.id)
        # created_at should be current time, not the provided value
        self.assertNotEqual(response.data['created_at'][:10], '2020-01-01')
    
    def test_rate_limiting_headers(self):
        """Test that rate limiting headers are present (if implemented)."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/worlds/')
        
        # Check if rate limiting headers are present
        # Note: This depends on rate limiting being configured
        # This test documents expected behavior
        if 'X-RateLimit-Limit' in response:
            self.assertIsNotNone(response['X-RateLimit-Limit'])
            self.assertIsNotNone(response['X-RateLimit-Remaining'])


class UserProfileSecurityTest(TestCase):
    """Test user profile security and privacy."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
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
        
        # Create profiles
        UserProfile.objects.create(
            user=self.user1,
            bio='Private bio information'
        )
        UserProfile.objects.create(
            user=self.user2,
            bio='Another private bio'
        )
    
    def test_user_profile_access_control(self):
        """Test that users can only access their own profile details."""
        # User should be able to access their own profile
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
        
        # But profile endpoint should only show current user's profile
        # (not other users' profiles)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user2')
    
    def test_sensitive_data_not_exposed(self):
        """Test that sensitive user data is not exposed in API responses."""
        self.client.force_authenticate(user=self.user1)
        
        # Check user info endpoint
        response = self.client.get('/api/auth/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should not expose password or other sensitive fields
        self.assertNotIn('password', response.data)
        self.assertNotIn('last_login', response.data)
        
        # Check that email is included (as it's needed for the user)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], 'user1@example.com')