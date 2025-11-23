"""
Settings package for worldbuilding project.
Automatically loads the appropriate settings module based on DJANGO_ENV.
"""

import os
from decouple import config

# Determine which settings to use
env = config('DJANGO_ENV', default='development')

if env == 'production':
    from .production import *
elif env == 'development':
    from .development import *
else:
    from .base import *
