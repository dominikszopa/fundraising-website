import os
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand
from team_fundraising.models import Fundraiser


class Command(BaseCommand):
    help = 'Generates lower-resolution versions of all photos'

    def handle(self, *args, **options):
        # Iterate over all Fundraiser instances
        for fundraiser in Fundraiser.objects.all():
            try:

                self.stdout.write(
                    self.style.NOTICE(
                        f"Generating lower-res version of photo for fundraiser '{fundraiser.name}'"
                    )
                )

                if fundraiser.photo:

                    # Open the original photo
                    with Image.open(fundraiser.photo.path) as img:
                        # Create a lower-resolution version
                        img.thumbnail((800, 800))

                        # Save the lower-resolution version
                        photo_dir, photo_filename = os.path.split(fundraiser.photo.name)
                        new_photo_path = os.path.join('photos_small', photo_filename)
                        img.save(os.path.join(settings.MEDIA_ROOT, new_photo_path))

                        # Update the photo_800 field to point to the new path
                        fundraiser.photo_small.name = new_photo_path
                        fundraiser.save()

            except FileNotFoundError:
                self.stdout.write(
                    self.style.WARNING(
                        f"File not found for fundraiser '{fundraiser.name}'"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully generated lower-resolution versions of all photos'
            )
        )
