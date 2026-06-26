import os
from django.apps import AppConfig
from django.conf import settings


class TeamFundraisingConfig(AppConfig):
    name = 'team_fundraising'

    def ready(self):
        from paypal.standard.ipn.signals import valid_ipn_received
        from .paypal import process_paypal
        valid_ipn_received.connect(process_paypal)

        # Create local media directories if they don't exist. Skipped when
        # media is stored in S3 (django-storages), where these local paths are
        # unused and creating them on the container is pointless.
        default_backend = settings.STORAGES.get('default', {}).get('BACKEND', '')
        if 'FileSystemStorage' in default_backend:
            photos_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
            photos_small_dir = os.path.join(settings.MEDIA_ROOT, 'photos_small')
            os.makedirs(photos_dir, exist_ok=True)
            os.makedirs(photos_small_dir, exist_ok=True)
