"""
Custom permissions for the collaborative worldbuilding application.
"""
from rest_framework import permissions


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit or delete it.
    Read-only access is allowed for any authenticated user.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the object.
        return obj.creator == request.user


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of content to edit or delete it.
    Read-only access is allowed for any authenticated user.
    Used for content models that have an 'author' field instead of 'creator'.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the content.
        return obj.author == request.user