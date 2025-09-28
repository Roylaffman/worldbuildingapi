"""
URL configuration for the collab app.
Defines versioned API endpoints for authentication and content management.
Implements proper HTTP method routing for immutability enforcement.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .views.auth import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    PasswordChangeView,
    LogoutView,
    user_info,
    verify_token
)
from .views.world_views import WorldViewSet
from .views.content_views import (
    PageViewSet, EssayViewSet, CharacterViewSet, 
    StoryViewSet, ImageViewSet
)
from .views.tagging_views import TagViewSet, ContentLinkViewSet

@api_view(['GET'])
@permission_classes([AllowAny])
def api_health(request):
    """Health check endpoint for API monitoring."""
    return Response({
        'status': 'healthy',
        'version': 'v1',
        'service': 'collaborative-worldbuilding-api',
        'timestamp': request.META.get('HTTP_DATE', 'unknown')
    }, status=status.HTTP_200_OK)

class ImmutableContentRouter(DefaultRouter):
    """
    Custom router that enforces immutability by restricting HTTP methods
    for content endpoints while allowing full CRUD for management endpoints.
    """
    
    def get_method_map(self, viewset, method_map):
        """
        Override method map to enforce immutability for content ViewSets.
        Content can only be created (POST) and read (GET), not updated or deleted.
        """
        # Get the standard method map
        bound_methods = super().get_method_map(viewset, method_map)
        
        # Check if this is a content ViewSet (immutable content)
        content_viewsets = [PageViewSet, EssayViewSet, CharacterViewSet, StoryViewSet, ImageViewSet]
        
        if any(isinstance(viewset, vs) for vs in content_viewsets):
            # For content ViewSets, only allow GET and POST methods
            # Remove PUT, PATCH, DELETE to enforce immutability
            immutable_methods = {}
            for method, action in bound_methods.items():
                if method in ['get', 'post']:
                    immutable_methods[method] = action
            return immutable_methods
        
        # For non-content ViewSets (worlds, tags, links), allow all methods
        return bound_methods

# Create custom router for ViewSets with immutability enforcement
router = ImmutableContentRouter()

# World management (full CRUD allowed)
router.register(r'worlds', WorldViewSet, basename='world')

# Content ViewSets (immutable - only GET and POST allowed)
router.register(r'pages', PageViewSet, basename='page')
router.register(r'essays', EssayViewSet, basename='essay')
router.register(r'characters', CharacterViewSet, basename='character')
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'images', ImageViewSet, basename='image')

# Tagging and linking ViewSets (full CRUD allowed for management)
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'links', ContentLinkViewSet, basename='contentlink')

# Authentication URL patterns
auth_urlpatterns = [
    # JWT Token Management
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='v1_token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='v1_token_refresh'),
    path('auth/verify/', verify_token, name='v1_token_verify'),
    
    # User Account Management
    path('auth/register/', UserRegistrationView.as_view(), name='v1_user_register'),
    path('auth/logout/', LogoutView.as_view(), name='v1_user_logout'),
    path('auth/user/', user_info, name='v1_user_info'),
    path('auth/profile/', UserProfileView.as_view(), name='v1_user_profile'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='v1_change_password'),
]

# World-scoped content URL patterns with immutability enforcement
content_urlpatterns = [
    # === IMMUTABLE CONTENT ENDPOINTS ===
    # Pages (Wiki Entries) - Only GET and POST allowed
    path('worlds/<int:world_pk>/pages/', 
         PageViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='v1_world_pages_list'),
    path('worlds/<int:world_pk>/pages/<int:pk>/', 
         PageViewSet.as_view({'get': 'retrieve'}), 
         name='v1_world_pages_detail'),
    path('worlds/<int:world_pk>/pages/<int:pk>/attribution_details/', 
         PageViewSet.as_view({'get': 'attribution_details'}), 
         name='v1_world_pages_attribution_details'),
    path('worlds/<int:world_pk>/pages/search-by-tags/', 
         PageViewSet.as_view({'get': 'search_by_tags'}), 
         name='v1_world_pages_search_by_tags'),
    path('worlds/<int:world_pk>/pages/chronological/', 
         PageViewSet.as_view({'get': 'chronological'}), 
         name='v1_world_pages_chronological'),
    
    # Essays (Long-form Content) - Only GET and POST allowed
    path('worlds/<int:world_pk>/essays/', 
         EssayViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='v1_world_essays_list'),
    path('worlds/<int:world_pk>/essays/<int:pk>/', 
         EssayViewSet.as_view({'get': 'retrieve'}), 
         name='v1_world_essays_detail'),
    path('worlds/<int:world_pk>/essays/search-by-tags/', 
         EssayViewSet.as_view({'get': 'search_by_tags'}), 
         name='v1_world_essays_search_by_tags'),
    path('worlds/<int:world_pk>/essays/chronological/', 
         EssayViewSet.as_view({'get': 'chronological_content'}), 
         name='v1_world_essays_chronological'),
    
    # Characters (Character Profiles) - Only GET and POST allowed
    path('worlds/<int:world_pk>/characters/', 
         CharacterViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='v1_world_characters_list'),
    path('worlds/<int:world_pk>/characters/<int:pk>/', 
         CharacterViewSet.as_view({'get': 'retrieve'}), 
         name='v1_world_characters_detail'),
    path('worlds/<int:world_pk>/characters/<int:pk>/attribution_details/', 
         CharacterViewSet.as_view({'get': 'attribution_details'}), 
         name='v1_world_characters_attribution_details'),
    path('worlds/<int:world_pk>/characters/search-by-tags/', 
         CharacterViewSet.as_view({'get': 'search_by_tags'}), 
         name='v1_world_characters_search_by_tags'),
    path('worlds/<int:world_pk>/characters/chronological/', 
         CharacterViewSet.as_view({'get': 'chronological_content'}), 
         name='v1_world_characters_chronological'),
    
    # Stories (Narrative Content) - Only GET and POST allowed
    path('worlds/<int:world_pk>/stories/', 
         StoryViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='v1_world_stories_list'),
    path('worlds/<int:world_pk>/stories/<int:pk>/', 
         StoryViewSet.as_view({'get': 'retrieve'}), 
         name='v1_world_stories_detail'),
    path('worlds/<int:world_pk>/stories/search-by-tags/', 
         StoryViewSet.as_view({'get': 'search_by_tags'}), 
         name='v1_world_stories_search_by_tags'),
    path('worlds/<int:world_pk>/stories/chronological/', 
         StoryViewSet.as_view({'get': 'chronological_content'}), 
         name='v1_world_stories_chronological'),
    
    # Images (Visual Content) - Only GET and POST allowed
    path('worlds/<int:world_pk>/images/', 
         ImageViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='v1_world_images_list'),
    path('worlds/<int:world_pk>/images/<int:pk>/', 
         ImageViewSet.as_view({'get': 'retrieve'}), 
         name='v1_world_images_detail'),
    path('worlds/<int:world_pk>/images/search-by-tags/', 
         ImageViewSet.as_view({'get': 'search_by_tags'}), 
         name='v1_world_images_search_by_tags'),
    path('worlds/<int:world_pk>/images/chronological/', 
         ImageViewSet.as_view({'get': 'chronological_content'}), 
         name='v1_world_images_chronological'),
    
    # === CONTENT RELATIONSHIP MANAGEMENT ===
    # Tag Management for Content (POST only - adding tags)
    path('worlds/<int:world_pk>/pages/<int:pk>/add-tags/', 
         PageViewSet.as_view({'post': 'add_tags'}), 
         name='v1_page_add_tags'),
    path('worlds/<int:world_pk>/essays/<int:pk>/add-tags/', 
         EssayViewSet.as_view({'post': 'add_tags'}), 
         name='v1_essay_add_tags'),
    path('worlds/<int:world_pk>/characters/<int:pk>/add-tags/', 
         CharacterViewSet.as_view({'post': 'add_tags'}), 
         name='v1_character_add_tags'),
    path('worlds/<int:world_pk>/stories/<int:pk>/add-tags/', 
         StoryViewSet.as_view({'post': 'add_tags'}), 
         name='v1_story_add_tags'),
    path('worlds/<int:world_pk>/images/<int:pk>/add-tags/', 
         ImageViewSet.as_view({'post': 'add_tags'}), 
         name='v1_image_add_tags'),
    
    # Link Management for Content (POST only - adding links)
    path('worlds/<int:world_pk>/pages/<int:pk>/add-links/', 
         PageViewSet.as_view({'post': 'add_links'}), 
         name='v1_page_add_links'),
    path('worlds/<int:world_pk>/essays/<int:pk>/add-links/', 
         EssayViewSet.as_view({'post': 'add_links'}), 
         name='v1_essay_add_links'),
    path('worlds/<int:world_pk>/characters/<int:pk>/add-links/', 
         CharacterViewSet.as_view({'post': 'add_links'}), 
         name='v1_character_add_links'),
    path('worlds/<int:world_pk>/stories/<int:pk>/add-links/', 
         StoryViewSet.as_view({'post': 'add_links'}), 
         name='v1_story_add_links'),
    path('worlds/<int:world_pk>/images/<int:pk>/add-links/', 
         ImageViewSet.as_view({'post': 'add_links'}), 
         name='v1_image_add_links'),
]

# Tag and Link management URL patterns (full CRUD allowed)
management_urlpatterns = [
    # === TAG MANAGEMENT ===
    # Tags can be managed (created, updated, deleted) as they're organizational tools
    path('worlds/<int:world_pk>/tags/', 
         TagViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='v1_world_tags_list'),
    path('worlds/<int:world_pk>/tags/<int:pk>/', 
         TagViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), 
         name='v1_world_tags_detail'),
    path('worlds/<int:world_pk>/tags/<int:pk>/content/', 
         TagViewSet.as_view({'get': 'content'}), 
         name='v1_world_tags_content'),
    path('worlds/<int:world_pk>/tags/popular/', 
         TagViewSet.as_view({'get': 'popular'}), 
         name='v1_world_tags_popular'),
    path('worlds/<int:world_pk>/tags/search-content/', 
         TagViewSet.as_view({'get': 'search_content'}), 
         name='v1_world_tags_search_content'),
    
    # === CONTENT LINK MANAGEMENT ===
    # Links can be managed (created, deleted) but not updated
    path('worlds/<int:world_pk>/links/', 
         ContentLinkViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='v1_world_links_list'),
    path('worlds/<int:world_pk>/links/<int:pk>/', 
         ContentLinkViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), 
         name='v1_world_links_detail'),
    path('worlds/<int:world_pk>/links/for-content/', 
         ContentLinkViewSet.as_view({'get': 'for_content'}), 
         name='v1_world_links_for_content'),
    path('worlds/<int:world_pk>/links/bulk-create/', 
         ContentLinkViewSet.as_view({'post': 'bulk_create'}), 
         name='v1_world_links_bulk_create'),
]

# Main URL patterns for API v1
urlpatterns = [
    # === API HEALTH AND STATUS ===
    path('health/', api_health, name='v1_api_health'),
    
    # === AUTHENTICATION ENDPOINTS ===
    path('', include(auth_urlpatterns)),
    
    # === CORE RESOURCE ENDPOINTS ===
    # World management and router-based endpoints (includes worlds, pages, essays, etc.)
    path('', include(router.urls)),
    
    # === WORLD-SCOPED CONTENT ENDPOINTS ===
    # Immutable content creation and retrieval within worlds
    path('', include(content_urlpatterns)),
    
    # === MANAGEMENT ENDPOINTS ===
    # Tag and link management (mutable organizational tools)
    path('', include(management_urlpatterns)),
]