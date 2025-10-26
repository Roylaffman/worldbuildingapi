#!/usr/bin/env python
"""
Simple script to test URL resolution
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'worldbuilding.settings')
sys.path.append('.')

django.setup()

from django.urls import get_resolver
from django.conf import settings

def print_urls(urlpatterns, prefix=''):
    """Print all URL patterns"""
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # This is an include() pattern
            print(f"{prefix}{pattern.pattern} -> INCLUDE")
            print_urls(pattern.url_patterns, prefix + "  ")
        else:
            # This is a regular pattern
            name = getattr(pattern, 'name', 'NO_NAME')
            print(f"{prefix}{pattern.pattern} -> {name}")

if __name__ == '__main__':
    resolver = get_resolver()
    print("URL Patterns:")
    print("=" * 50)
    print_urls(resolver.url_patterns)