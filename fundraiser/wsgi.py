"""
WSGI config for fundraiser project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundraiser.settings')

application = get_wsgi_application()

# Configure WhiteNoise to serve media files in production
# Media files are served from the /media/ URL path
# Using shorter cache time for media files since they can be updated
from django.conf import settings
application = WhiteNoise(
    application,
    root=settings.MEDIA_ROOT,
    prefix=settings.MEDIA_URL.strip('/'),
    max_age=3600  # 1 hour cache for media files (vs 1 year for static)
)
