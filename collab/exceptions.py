"""
Custom exceptions and exception handlers for the collaborative worldbuilding API.
Provides meaningful error messages and proper HTTP status codes.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from django.core.files.uploadedfile import UploadedFile
import logging

logger = logging.getLogger(__name__)


class ImmutabilityViolationError(Exception):
    """
    Exception raised when attempting to modify immutable content.
    """
    def __init__(self, message="Content cannot be modified after creation", content_type=None, content_id=None):
        self.message = message
        self.content_type = content_type
        self.content_id = content_id
        super().__init__(self.message)


class ContentValidationError(Exception):
    """
    Exception raised when content validation fails.
    """
    def __init__(self, message, field=None, code=None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)


class FileUploadError(Exception):
    """
    Exception raised when file upload validation fails.
    """
    def __init__(self, message, file_name=None, file_size=None, file_type=None):
        self.message = message
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type
        super().__init__(self.message)


class WorldAccessError(Exception):
    """
    Exception raised when user doesn't have access to a world or world doesn't exist.
    """
    def __init__(self, message="World not found or access denied", world_id=None):
        self.message = message
        self.world_id = world_id
        super().__init__(self.message)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    for the collaborative worldbuilding API.
    """
    # Get the standard error response first
    response = exception_handler(exc, context)
    
    # Get request information
    request = context.get('request')
    view = context.get('view')
    
    # Create base error data
    error_data = {
        'timestamp': request.META.get('HTTP_DATE') if request else None,
        'path': request.path if request else None,
        'method': request.method if request else None,
        'api_version': getattr(request, 'api_version', 'v1') if request else 'v1',
    }
    
    # Handle custom exceptions
    if isinstance(exc, ImmutabilityViolationError):
        error_data.update({
            'error': 'Immutability Violation',
            'message': exc.message,
            'detail': 'Content is immutable after creation to maintain chronological integrity',
            'content_type': exc.content_type,
            'content_id': exc.content_id,
            'suggestion': 'Create new content instead of modifying existing content',
            'allowed_operations': ['GET', 'POST']
        })
        response = Response(error_data, status=status.HTTP_409_CONFLICT)
        
    elif isinstance(exc, ContentValidationError):
        error_data.update({
            'error': 'Content Validation Error',
            'message': exc.message,
            'field': exc.field,
            'code': exc.code,
            'suggestion': 'Please check your input data and try again'
        })
        response = Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(exc, FileUploadError):
        error_data.update({
            'error': 'File Upload Error',
            'message': exc.message,
            'file_name': exc.file_name,
            'file_size': exc.file_size,
            'file_type': exc.file_type,
            'suggestion': 'Please check file size, type, and format requirements'
        })
        response = Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(exc, WorldAccessError):
        error_data.update({
            'error': 'World Access Error',
            'message': exc.message,
            'world_id': exc.world_id,
            'suggestion': 'Verify the world ID and your access permissions'
        })
        response = Response(error_data, status=status.HTTP_404_NOT_FOUND)
    
    # Handle Django validation errors
    elif isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            # Field-specific validation errors
            error_data.update({
                'error': 'Validation Error',
                'message': 'One or more fields failed validation',
                'field_errors': exc.message_dict,
                'suggestion': 'Please correct the highlighted fields and try again'
            })
        else:
            # General validation errors
            error_data.update({
                'error': 'Validation Error',
                'message': str(exc),
                'suggestion': 'Please check your input data and try again'
            })
        response = Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle database integrity errors
    elif isinstance(exc, IntegrityError):
        error_message = str(exc)
        
        # Parse common integrity constraint violations
        if 'unique constraint' in error_message.lower():
            error_data.update({
                'error': 'Duplicate Entry',
                'message': 'A record with this information already exists',
                'detail': 'Unique constraint violation',
                'suggestion': 'Please use different values for unique fields'
            })
        elif 'foreign key constraint' in error_message.lower():
            error_data.update({
                'error': 'Invalid Reference',
                'message': 'Referenced record does not exist',
                'detail': 'Foreign key constraint violation',
                'suggestion': 'Please ensure all referenced records exist'
            })
        else:
            error_data.update({
                'error': 'Database Constraint Violation',
                'message': 'Database operation failed due to constraint violation',
                'detail': str(exc),
                'suggestion': 'Please check your data and try again'
            })
        
        response = Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle 404 errors
    elif isinstance(exc, Http404):
        error_data.update({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'suggestion': 'Please check the URL and resource ID'
        })
        response = Response(error_data, status=status.HTTP_404_NOT_FOUND)
    
    # Enhance existing DRF error responses
    elif response is not None:
        custom_data = error_data.copy()
        
        # Add context to existing error responses
        if response.status_code == 400:
            custom_data.update({
                'error': 'Bad Request',
                'message': 'Invalid request data',
                'detail': response.data,
                'suggestion': 'Please check your request format and data'
            })
        elif response.status_code == 401:
            custom_data.update({
                'error': 'Authentication Required',
                'message': 'Valid authentication credentials are required',
                'detail': response.data,
                'suggestion': 'Please provide valid JWT token in Authorization header'
            })
        elif response.status_code == 403:
            custom_data.update({
                'error': 'Permission Denied',
                'message': 'You do not have permission to perform this action',
                'detail': response.data,
                'suggestion': 'Please check your permissions or contact an administrator'
            })
        elif response.status_code == 404:
            custom_data.update({
                'error': 'Not Found',
                'message': 'The requested resource was not found',
                'detail': response.data,
                'suggestion': 'Please check the URL and resource ID'
            })
        elif response.status_code == 405:
            custom_data.update({
                'error': 'Method Not Allowed',
                'message': 'HTTP method not allowed for this endpoint',
                'detail': response.data,
                'allowed_methods': response.get('Allow', '').split(', ') if response.get('Allow') else [],
                'suggestion': 'Please use one of the allowed HTTP methods'
            })
        elif response.status_code == 429:
            custom_data.update({
                'error': 'Rate Limit Exceeded',
                'message': 'Too many requests',
                'detail': response.data,
                'suggestion': 'Please wait before making more requests'
            })
        else:
            custom_data.update({
                'error': 'API Error',
                'message': 'An error occurred while processing your request',
                'detail': response.data
            })
        
        response.data = custom_data
    
    # Handle unexpected errors
    else:
        error_data.update({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'detail': str(exc) if str(exc) else 'Unknown error',
            'suggestion': 'Please try again later or contact support if the problem persists'
        })
        response = Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Log the error for monitoring
    if response and response.status_code >= 500:
        logger.error(f"API Error: {exc}", exc_info=True, extra={
            'request_path': request.path if request else None,
            'request_method': request.method if request else None,
            'user': request.user.username if request and hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
            'view': view.__class__.__name__ if view else None,
        })
    elif response and response.status_code >= 400:
        logger.warning(f"API Client Error: {exc}", extra={
            'request_path': request.path if request else None,
            'request_method': request.method if request else None,
            'user': request.user.username if request and hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
            'status_code': response.status_code,
        })
    
    return response


def validate_file_upload(uploaded_file, max_size_mb=10, allowed_types=None):
    """
    Validate uploaded files for size, type, and other constraints.
    
    Args:
        uploaded_file: Django UploadedFile instance
        max_size_mb: Maximum file size in MB
        allowed_types: List of allowed MIME types
    
    Raises:
        FileUploadError: If validation fails
    """
    # Check if it's a valid uploaded file (including test files)
    if not hasattr(uploaded_file, 'size') or not hasattr(uploaded_file, 'name'):
        raise FileUploadError("Invalid file upload")
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        raise FileUploadError(
            f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)",
            file_name=uploaded_file.name,
            file_size=uploaded_file.size
        )
    
    # Check file type
    if allowed_types and hasattr(uploaded_file, 'content_type'):
        if uploaded_file.content_type not in allowed_types:
            raise FileUploadError(
                f"File type '{uploaded_file.content_type}' is not allowed. Allowed types: {', '.join(allowed_types)}",
                file_name=uploaded_file.name,
                file_type=uploaded_file.content_type
            )
    
    # Check for empty files
    if uploaded_file.size == 0:
        raise FileUploadError(
            "Empty files are not allowed",
            file_name=uploaded_file.name,
            file_size=uploaded_file.size
        )
    
    # Basic file name validation
    if not uploaded_file.name or len(uploaded_file.name.strip()) == 0:
        raise FileUploadError("File must have a valid name")
    
    # Check for potentially dangerous file extensions
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js', '.jar']
    file_extension = uploaded_file.name.lower().split('.')[-1] if '.' in uploaded_file.name else ''
    if f'.{file_extension}' in dangerous_extensions:
        raise FileUploadError(
            f"File extension '.{file_extension}' is not allowed for security reasons",
            file_name=uploaded_file.name
        )
    
    return True