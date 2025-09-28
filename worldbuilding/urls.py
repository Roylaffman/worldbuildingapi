"""
URL configuration for worldbuilding project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint that provides comprehensive information about available endpoints.
    This serves as the main entry point for API discovery.
    """
    return Response({
        'message': 'Collaborative Worldbuilding API',
        'version': 'v1',
        'description': 'RESTful API for collaborative worldbuilding with immutable content',
        'documentation': {
            'api_root': request.build_absolute_uri('/api/'),
            'admin': request.build_absolute_uri('/admin/'),
            'schema': request.build_absolute_uri('/api/schema/'),
        },
        'endpoints': {
            'authentication': {
                'description': 'JWT-based authentication endpoints',
                'login': request.build_absolute_uri('/api/v1/auth/login/'),
                'register': request.build_absolute_uri('/api/v1/auth/register/'),
                'refresh_token': request.build_absolute_uri('/api/v1/auth/refresh/'),
                'verify_token': request.build_absolute_uri('/api/v1/auth/verify/'),
                'user_info': request.build_absolute_uri('/api/v1/auth/user/'),
                'profile': request.build_absolute_uri('/api/v1/auth/profile/'),
                'change_password': request.build_absolute_uri('/api/v1/auth/change-password/'),
                'logout': request.build_absolute_uri('/api/v1/auth/logout/'),
            },
            'worlds': {
                'description': 'World management and content organization',
                'list_create': request.build_absolute_uri('/api/v1/worlds/'),
                'detail': request.build_absolute_uri('/api/v1/worlds/{id}/'),
                'timeline': request.build_absolute_uri('/api/v1/worlds/{id}/timeline/'),
                'search': request.build_absolute_uri('/api/v1/worlds/{id}/search/'),
                'statistics': request.build_absolute_uri('/api/v1/worlds/{id}/statistics/'),
                'related_content': request.build_absolute_uri('/api/v1/worlds/{id}/related_content/'),
            },
            'content': {
                'description': 'Immutable content creation within worlds',
                'pages': request.build_absolute_uri('/api/v1/worlds/{world_id}/pages/'),
                'essays': request.build_absolute_uri('/api/v1/worlds/{world_id}/essays/'),
                'characters': request.build_absolute_uri('/api/v1/worlds/{world_id}/characters/'),
                'stories': request.build_absolute_uri('/api/v1/worlds/{world_id}/stories/'),
                'images': request.build_absolute_uri('/api/v1/worlds/{world_id}/images/'),
            },
            'tagging_linking': {
                'description': 'Tag and link management for content relationships',
                'tags': request.build_absolute_uri('/api/v1/worlds/{world_id}/tags/'),
                'links': request.build_absolute_uri('/api/v1/worlds/{world_id}/links/'),
                'add_tags': request.build_absolute_uri('/api/v1/worlds/{world_id}/{content_type}/{id}/add-tags/'),
                'add_links': request.build_absolute_uri('/api/v1/worlds/{world_id}/{content_type}/{id}/add-links/'),
            }
        },
        'features': {
            'immutable_content': 'All content is immutable after creation to maintain chronological integrity',
            'jwt_authentication': 'Secure JWT-based authentication with refresh tokens',
            'world_scoped': 'All content is scoped to specific worlds for organization',
            'bidirectional_links': 'Content can be linked bidirectionally for rich relationships',
            'tag_based_search': 'Powerful search and filtering based on tags and content',
            'chronological_timeline': 'Timeline view maintains creation order for world development',
        },
        'http_methods': {
            'GET': 'Retrieve resources (always allowed)',
            'POST': 'Create new resources (content becomes immutable)',
            'PUT': 'Not allowed for content (immutability enforcement)',
            'PATCH': 'Not allowed for content (immutability enforcement)',
            'DELETE': 'Not allowed for content (immutability enforcement)',
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_schema(request):
    """
    API schema endpoint that provides OpenAPI-style schema information.
    """
    return Response({
        'openapi': '3.0.0',
        'info': {
            'title': 'Collaborative Worldbuilding API',
            'version': 'v1',
            'description': 'RESTful API for collaborative worldbuilding with immutable content and chronological integrity',
            'contact': {
                'name': 'API Support',
            }
        },
        'servers': [
            {
                'url': request.build_absolute_uri('/api/v1/'),
                'description': 'Production server'
            }
        ],
        'paths': {
            '/auth/': 'Authentication endpoints',
            '/worlds/': 'World management endpoints',
            '/worlds/{world_id}/pages/': 'Page content endpoints',
            '/worlds/{world_id}/essays/': 'Essay content endpoints',
            '/worlds/{world_id}/characters/': 'Character content endpoints',
            '/worlds/{world_id}/stories/': 'Story content endpoints',
            '/worlds/{world_id}/images/': 'Image content endpoints',
            '/worlds/{world_id}/tags/': 'Tag management endpoints',
            '/worlds/{world_id}/links/': 'Content link management endpoints',
        },
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        },
        'security': [
            {
                'bearerAuth': []
            }
        ]
    }, status=status.HTTP_200_OK)

urlpatterns = [
    # API Root and Documentation
    path('', api_root, name='api_root'),
    path('api/', api_root, name='api_root_v2'),
    path('api/schema/', api_schema, name='api_schema'),
    
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # API Version 1 (Current)
    path('api/v1/', include('collab.urls')),
    
    # Backward compatibility (will be deprecated)
    path('api/', include('collab.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
