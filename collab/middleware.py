"""
Custom middleware for the collaborative worldbuilding API.
Handles API versioning, CORS, and immutability enforcement.
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
import json


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning and add version headers to responses.
    """
    
    def process_request(self, request):
        """Add API version information to the request."""
        # Determine API version from URL path
        if request.path.startswith('/api/v1/'):
            request.api_version = 'v1'
        elif request.path.startswith('/api/') and not request.path.startswith('/api/v'):
            request.api_version = 'v1'  # Default to v1 for backward compatibility
        else:
            request.api_version = None
        
        return None
    
    def process_response(self, request, response):
        """Add API version headers to responses."""
        if hasattr(request, 'api_version') and request.api_version:
            response['X-API-Version'] = request.api_version
            response['X-API-Service'] = 'collaborative-worldbuilding'
        
        return response


class ImmutabilityEnforcementMiddleware(MiddlewareMixin):
    """
    Middleware to enforce immutability rules for content endpoints.
    Blocks PUT, PATCH, and DELETE requests to immutable content.
    """
    
    # Define immutable content endpoints patterns
    IMMUTABLE_PATTERNS = [
        '/api/v1/worlds/',
        '/api/v1/pages/',
        '/api/v1/essays/',
        '/api/v1/characters/',
        '/api/v1/stories/',
        '/api/v1/images/',
        '/api/worlds/',  # Backward compatibility
        '/api/pages/',
        '/api/essays/',
        '/api/characters/',
        '/api/stories/',
        '/api/images/',
    ]
    
    # Define content-specific patterns that should be immutable
    CONTENT_PATTERNS = [
        'pages',
        'essays', 
        'characters',
        'stories',
        'images'
    ]
    
    def process_request(self, request):
        """
        Check if the request violates immutability rules and block if necessary.
        """
        # Only check for modification methods
        if request.method not in ['PUT', 'PATCH', 'DELETE']:
            return None
        
        # Check if this is a content endpoint
        path = request.path.lower()
        
        # Check for direct content modification
        for pattern in self.CONTENT_PATTERNS:
            if f'/{pattern}/' in path and request.method in ['PUT', 'PATCH', 'DELETE']:
                # Allow DELETE for links and tags management, but not for content itself
                if '/add-tags/' in path or '/add-links/' in path:
                    continue
                if '/tags/' in path or '/links/' in path:
                    continue
                
                # Block modification of immutable content
                return JsonResponse({
                    'error': 'Immutability Violation',
                    'message': f'{request.method} method not allowed for immutable content',
                    'detail': f'Content of type "{pattern}" cannot be modified after creation to maintain chronological integrity',
                    'allowed_methods': ['GET', 'POST'],
                    'endpoint': path,
                    'timestamp': request.META.get('HTTP_DATE', 'unknown'),
                    'suggestion': 'Create new content instead of modifying existing content'
                }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        return None


class APIDocumentationMiddleware(MiddlewareMixin):
    """
    Middleware to add API documentation headers and handle OPTIONS requests.
    """
    
    def process_request(self, request):
        """Handle OPTIONS requests for API documentation."""
        if request.method == 'OPTIONS' and request.path.startswith('/api/'):
            # Determine allowed methods based on endpoint type
            path = request.path.lower()
            
            # Default allowed methods
            allowed_methods = ['GET', 'POST', 'OPTIONS']
            
            # Check if this is a management endpoint (tags, links, worlds)
            if any(pattern in path for pattern in ['/tags/', '/links/', '/worlds/']):
                # Management endpoints allow full CRUD
                if '/worlds/' in path and path.count('/') == 4:  # World detail endpoint
                    allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
                elif '/tags/' in path or '/links/' in path:
                    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
                else:
                    allowed_methods = ['GET', 'POST', 'OPTIONS']
            
            # Check if this is immutable content
            content_patterns = ['pages', 'essays', 'characters', 'stories', 'images']
            if any(pattern in path for pattern in content_patterns):
                allowed_methods = ['GET', 'POST', 'OPTIONS']
            
            response = JsonResponse({
                'message': 'API endpoint information',
                'allowed_methods': allowed_methods,
                'api_version': 'v1',
                'immutable_content': any(pattern in path for pattern in content_patterns),
                'documentation': request.build_absolute_uri('/api/schema/')
            })
            
            response['Allow'] = ', '.join(allowed_methods)
            response['X-API-Version'] = 'v1'
            response['X-Content-Immutable'] = str(any(pattern in path for pattern in content_patterns)).lower()
            
            return response
        
        return None
    
    def process_response(self, request, response):
        """Add documentation headers to API responses."""
        if request.path.startswith('/api/'):
            response['X-API-Documentation'] = request.build_absolute_uri('/api/schema/')
            response['X-API-Root'] = request.build_absolute_uri('/api/')
        
        return response


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to provide consistent error handling for API endpoints.
    """
    
    def process_exception(self, request, exception):
        """Handle exceptions and return consistent API error responses."""
        if not request.path.startswith('/api/'):
            return None
        
        # Handle common exceptions with proper API responses
        error_response = {
            'error': exception.__class__.__name__,
            'message': str(exception),
            'path': request.path,
            'method': request.method,
            'timestamp': request.META.get('HTTP_DATE', 'unknown'),
            'api_version': getattr(request, 'api_version', 'v1')
        }
        
        # Determine appropriate status code
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        if 'DoesNotExist' in exception.__class__.__name__:
            status_code = status.HTTP_404_NOT_FOUND
            error_response['error'] = 'Not Found'
        elif 'ValidationError' in exception.__class__.__name__:
            status_code = status.HTTP_400_BAD_REQUEST
            error_response['error'] = 'Validation Error'
        elif 'PermissionDenied' in exception.__class__.__name__:
            status_code = status.HTTP_403_FORBIDDEN
            error_response['error'] = 'Permission Denied'
        elif 'NotAuthenticated' in exception.__class__.__name__:
            status_code = status.HTTP_401_UNAUTHORIZED
            error_response['error'] = 'Authentication Required'
        
        response = JsonResponse(error_response, status=status_code)
        response['X-API-Version'] = getattr(request, 'api_version', 'v1')
        
        return response