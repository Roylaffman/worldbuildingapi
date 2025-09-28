"""
Custom validators for the collaborative worldbuilding application.
Provides reusable validation logic with meaningful error messages.
"""
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
import re


@deconstructible
class WorldTitleValidator:
    """
    Validator for world titles.
    Ensures titles are appropriate for public worldbuilding spaces.
    """
    
    def __init__(self, min_length=3, max_length=200):
        self.min_length = min_length
        self.max_length = max_length
    
    def __call__(self, value):
        if not value or not value.strip():
            raise ValidationError(
                "World title cannot be empty",
                code='required'
            )
        
        cleaned_value = value.strip()
        
        if len(cleaned_value) < self.min_length:
            raise ValidationError(
                f"World title must be at least {self.min_length} characters long",
                code='min_length',
                params={'min_length': self.min_length, 'current_length': len(cleaned_value)}
            )
        
        if len(cleaned_value) > self.max_length:
            raise ValidationError(
                f"World title cannot exceed {self.max_length} characters",
                code='max_length',
                params={'max_length': self.max_length, 'current_length': len(cleaned_value)}
            )
        
        # Check for inappropriate content (basic filter)
        inappropriate_patterns = [
            r'\b(spam|test123|asdf|qwerty)\b',
            r'^(untitled|new world|world \d+)$',
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, cleaned_value.lower()):
                raise ValidationError(
                    "Please choose a more descriptive world title",
                    code='inappropriate_title'
                )


@deconstructible
class ContentTitleValidator:
    """
    Validator for content titles.
    Ensures titles are descriptive and appropriate.
    """
    
    def __init__(self, min_length=3, max_length=300):
        self.min_length = min_length
        self.max_length = max_length
    
    def __call__(self, value):
        if not value or not value.strip():
            raise ValidationError(
                "Content title cannot be empty",
                code='required'
            )
        
        cleaned_value = value.strip()
        
        if len(cleaned_value) < self.min_length:
            raise ValidationError(
                f"Content title must be at least {self.min_length} characters long",
                code='min_length',
                params={'min_length': self.min_length, 'current_length': len(cleaned_value)}
            )
        
        if len(cleaned_value) > self.max_length:
            raise ValidationError(
                f"Content title cannot exceed {self.max_length} characters",
                code='max_length',
                params={'max_length': self.max_length, 'current_length': len(cleaned_value)}
            )


@deconstructible
class ContentBodyValidator:
    """
    Validator for content body text.
    Ensures content has sufficient substance.
    """
    
    def __init__(self, min_length=10, max_length=50000):
        self.min_length = min_length
        self.max_length = max_length
    
    def __call__(self, value):
        if not value or not value.strip():
            raise ValidationError(
                "Content body cannot be empty",
                code='required'
            )
        
        cleaned_value = value.strip()
        
        if len(cleaned_value) < self.min_length:
            raise ValidationError(
                f"Content must be at least {self.min_length} characters long",
                code='min_length',
                params={'min_length': self.min_length, 'current_length': len(cleaned_value)}
            )
        
        if len(cleaned_value) > self.max_length:
            raise ValidationError(
                f"Content cannot exceed {self.max_length} characters",
                code='max_length',
                params={'max_length': self.max_length, 'current_length': len(cleaned_value)}
            )


@deconstructible
class TagNameValidator:
    """
    Validator for tag names.
    Ensures tags follow naming conventions.
    """
    
    def __init__(self, min_length=2, max_length=100):
        self.min_length = min_length
        self.max_length = max_length
    
    def __call__(self, value):
        if not value or not value.strip():
            raise ValidationError(
                "Tag name cannot be empty",
                code='required'
            )
        
        cleaned_value = value.strip().lower()
        
        if len(cleaned_value) < self.min_length:
            raise ValidationError(
                f"Tag name must be at least {self.min_length} characters long",
                code='min_length',
                params={'min_length': self.min_length, 'current_length': len(cleaned_value)}
            )
        
        if len(cleaned_value) > self.max_length:
            raise ValidationError(
                f"Tag name cannot exceed {self.max_length} characters",
                code='max_length',
                params={'max_length': self.max_length, 'current_length': len(cleaned_value)}
            )
        
        # Check for valid tag format (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-z0-9\-_\s]+$', cleaned_value):
            raise ValidationError(
                "Tag names can only contain letters, numbers, hyphens, underscores, and spaces",
                code='invalid_format'
            )
        
        # Check for reserved tag names
        reserved_names = ['admin', 'system', 'api', 'null', 'undefined', 'delete', 'edit']
        if cleaned_value in reserved_names:
            raise ValidationError(
                f"'{cleaned_value}' is a reserved tag name",
                code='reserved_name'
            )


@deconstructible
class CharacterNameValidator:
    """
    Validator for character names.
    Ensures character names are appropriate for worldbuilding.
    """
    
    def __call__(self, value):
        if not value or not value.strip():
            raise ValidationError(
                "Character must have a name",
                code='required'
            )
        
        cleaned_value = value.strip()
        
        if len(cleaned_value) < 2:
            raise ValidationError(
                "Character name must be at least 2 characters long",
                code='min_length'
            )
        
        if len(cleaned_value) > 200:
            raise ValidationError(
                "Character name cannot exceed 200 characters",
                code='max_length'
            )
        
        # Basic format validation (allow most characters for fantasy names)
        if not re.match(r'^[a-zA-Z0-9\s\'\-\.]+$', cleaned_value):
            raise ValidationError(
                "Character names can only contain letters, numbers, spaces, apostrophes, hyphens, and periods",
                code='invalid_format'
            )


def validate_json_field(value, field_name, expected_type=None, max_items=None):
    """
    Validate JSON field data with specific constraints.
    
    Args:
        value: The JSON field value
        field_name: Name of the field for error messages
        expected_type: Expected Python type (list, dict, etc.)
        max_items: Maximum number of items for lists/dicts
    
    Raises:
        ValidationError: If validation fails
    """
    if expected_type and not isinstance(value, expected_type):
        raise ValidationError(
            f"{field_name} must be a {expected_type.__name__}",
            code='invalid_type'
        )
    
    if max_items and hasattr(value, '__len__') and len(value) > max_items:
        raise ValidationError(
            f"{field_name} cannot have more than {max_items} items",
            code='max_items',
            params={'max_items': max_items, 'current_items': len(value)}
        )
    
    # Validate list items if it's a list
    if isinstance(value, list):
        for i, item in enumerate(value):
            if not isinstance(item, str):
                raise ValidationError(
                    f"{field_name} items must be strings (item {i} is {type(item).__name__})",
                    code='invalid_item_type'
                )
            
            if not item.strip():
                raise ValidationError(
                    f"{field_name} cannot contain empty items",
                    code='empty_item'
                )
    
    # Validate dict values if it's a dict
    if isinstance(value, dict):
        for key, val in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValidationError(
                    f"{field_name} keys must be non-empty strings",
                    code='invalid_key'
                )
            
            if not isinstance(val, str):
                raise ValidationError(
                    f"{field_name} values must be strings",
                    code='invalid_value_type'
                )


def validate_world_membership(content_instance, world):
    """
    Validate that content belongs to the specified world.
    
    Args:
        content_instance: Content model instance
        world: World model instance
    
    Raises:
        ValidationError: If content doesn't belong to the world
    """
    if content_instance.world != world:
        raise ValidationError(
            f"Content does not belong to world '{world.title}'",
            code='world_mismatch'
        )