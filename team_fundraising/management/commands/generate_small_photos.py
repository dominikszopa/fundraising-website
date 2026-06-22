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

                    # Reuse the model's thumbnail logic (EXIF-aware) so this
                    # command stays in sync with what save() produces.
                    fundraiser._generate_thumbnail()
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
