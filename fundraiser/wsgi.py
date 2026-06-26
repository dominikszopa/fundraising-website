"""
WSGI config for fundraiser project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundraiser.settings')

application = get_wsgi_application()

# Configure WhiteNoise to serve media files from the local filesystem.
# Media files are served from the /media/ URL path with a shorter cache time
# since they can be updated. Skipped when media is stored in S3
# (django-storages): photo URLs then point directly at the bucket and there is
# nothing local to serve.
from django.conf import settings
if not getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''):
    from whitenoise import WhiteNoise
    application = WhiteNoise(
        application,
        root=settings.MEDIA_ROOT,
        prefix=settings.MEDIA_URL.strip('/'),
        max_age=3600,  # 1 hour cache for media files (vs 1 year for static)
        # re-scan disk per request so new uploads are served without a restart
        autorefresh=True,
    )
