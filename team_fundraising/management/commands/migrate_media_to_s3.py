"""
One-time management command to copy existing fundraiser/campaign media files
from the local filesystem (e.g. the Railway volume at MEDIA_ROOT) into the
configured default storage backend (S3 via django-storages).

Run this once after switching the default storage to S3 so that photos
uploaded before the migration keep working. It is idempotent: files already
present in the destination are skipped, so it is safe to re-run.

    python3 manage.py migrate_media_to_s3
    python3 manage.py migrate_media_to_s3 --dry-run
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.management.base import BaseCommand

from team_fundraising.models import Campaign, Fundraiser


class Command(BaseCommand):
    help = 'Copy existing media files from the local filesystem into S3.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List what would be uploaded without writing anything.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Source is always the local media directory; destination is whatever
        # the default storage is configured to be (S3 in production).
        source = FileSystemStorage(location=settings.MEDIA_ROOT)
        dest = default_storage

        # (model, field name) pairs that hold media files.
        targets = [
            (Fundraiser, 'photo'),
            (Fundraiser, 'photo_small'),
            (Campaign, 'photo'),
        ]

        # Collect unique file names so a name referenced by several rows is
        # only handled once.
        names = set()
        for model, field in targets:
            for value in (
                model.objects.exclude(**{field: ''})
                .exclude(**{f'{field}__isnull': True})
                .values_list(field, flat=True)
            ):
                if value:
                    names.add(value)

        uploaded = skipped = missing = 0

        for name in sorted(names):
            if not source.exists(name):
                self.stdout.write(
                    self.style.WARNING(f'MISSING source, skipping: {name}')
                )
                missing += 1
                continue

            if dest.exists(name):
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f'WOULD UPLOAD: {name}')
                uploaded += 1
                continue

            with source.open(name) as f:
                saved_name = dest.save(name, f)
            if saved_name != name:
                # file_overwrite=True keeps names stable on S3; warn if the
                # backend renamed the object so references are not silently lost.
                self.stdout.write(
                    self.style.WARNING(
                        f'Saved as {saved_name} (expected {name})'
                    )
                )
            self.stdout.write(self.style.SUCCESS(f'UPLOADED: {name}'))
            uploaded += 1

        verb = 'Would upload' if dry_run else 'Uploaded'
        self.stdout.write(
            self.style.SUCCESS(
                f'{verb} {uploaded}, skipped {skipped} (already present), '
                f'{missing} missing source file(s).'
            )
        )
