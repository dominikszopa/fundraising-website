import io
import os
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image
from ..models import Campaign, Fundraiser, Donation, Donor


class TestModels(TestCase):
    """ Parent class that builds all data for base model tests """

    @classmethod
    def setUpTestData(cls):
        campaign1 = Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='message',
            default_fundraiser_message='default message',
        )

        # A fundraiser with a few donations already
        fundraiser1 = Fundraiser.objects.create(
            campaign=campaign1,
            name='First Fundraiser',
            goal=200,
            photo='',
            message='You go dude!',
        )

        Donation.objects.create(
            fundraiser=fundraiser1,
            name='First Donator',
            amount=50.00,
            anonymous=False,
            email='name@domain.com',
            message='Good luck!',
            address='123 lane street',
            city='Vancouver',
            province='BC',
            country='Canada',
            postal_code='A0A 1B1',
            payment_method='paypal',
            payment_status='paid',
            date=timezone.now(),
        )

        Donation.objects.create(
            fundraiser=fundraiser1,
            name='First Donator',
            amount=33.00,
            anonymous=True,
            email='name@domain.com',
            message='Good luck!',
            address='123 lane street',
            city='Vancouver',
            province='BC',
            country='Canada',
            postal_code='A0A 1B1',
            payment_method='paypal',
            payment_status='paid',
            date=timezone.now(),
        )

        # an incomplete donation, which should not be counted in totals
        Donation.objects.create(
            fundraiser=fundraiser1,
            name='Incomplete donation',
            amount=10.00,
            anonymous=False,
            email='noncommital@issues.com',
            message='Almost',
            payment_method='paypal',
            payment_status='pending',
            date=timezone.now(),
        )

        # A fundraiser without donations
        Fundraiser.objects.create(
            campaign=campaign1,
            name='Empty Fundraiser',
            goal=100,
            photo='',
            photo_small='',
            message='Just starting!',
        )


class TestCampaignModel(TestModels):

    def test_name(self):
        """ Check the Campaign.__str__ function """
        campaign = Campaign.objects.first()
        self.assertEqual(str(campaign), 'Test Campaign')

    def test_donation_total(self):
        """ Verify total donations sum is correct """
        campaign = Campaign.objects.first()
        total = campaign.get_total_raised()
        self.assertEqual(total, 83.00)


class TestFundraiser(TestModels):

    def test_name(self):
        """ Check the Fundraiser .__str__ function """
        fundraiser = Fundraiser.objects.first()
        self.assertEqual(str(fundraiser), 'First Fundraiser')

    def test_donation_total(self):
        """ Verify total donations for fundraiser is correct """
        fundraiser = Fundraiser.objects.first()
        total = fundraiser.total_raised()
        self.assertEqual(total, 83.00)

    def test_total_donators(self):
        """ Check the number of donators is correct """
        fundraiser = Fundraiser.objects.first()
        total = fundraiser.total_donations()
        self.assertEqual(total, 2)


class TestFundraiserPhoto(TestCase):
    """ Tests for photo thumbnailing and rotation """

    def _make_image_upload(self, width, height, color=(255, 0, 0)):
        """ Build an in-memory PNG upload of the given dimensions """
        buffer = io.BytesIO()
        Image.new('RGB', (width, height), color).save(buffer, format='PNG')
        buffer.seek(0)
        return SimpleUploadedFile(
            'test_photo.png', buffer.read(), content_type='image/png'
        )

    def setUp(self):
        self.campaign = Campaign.objects.create(
            name='Photo Campaign',
            goal=1000,
            campaign_message='message',
            default_fundraiser_message='default message',
        )

    def test_rotate_photo_swaps_dimensions_in_place(self):
        """
        Rotating a non-square photo 90 degrees swaps its width and height
        and overwrites the same file rather than creating a new one.
        """
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                fundraiser = Fundraiser.objects.create(
                    campaign=self.campaign,
                    name='Photo Fundraiser',
                    goal=100,
                    photo=self._make_image_upload(100, 60),
                )

                original_name = fundraiser.photo.name
                path = os.path.join(settings.MEDIA_ROOT, original_name)

                with Image.open(path) as img:
                    self.assertEqual(img.size, (100, 60))

                fundraiser.rotate_photo(90)
                fundraiser.save()

                # Same filename, no extra version created.
                self.assertEqual(fundraiser.photo.name, original_name)

                with Image.open(path) as img:
                    self.assertEqual(img.size, (60, 100))

    def test_thumbnail_generated_on_upload(self):
        """ Uploading a photo generates a matching photo_small thumbnail """
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                fundraiser = Fundraiser.objects.create(
                    campaign=self.campaign,
                    name='Photo Fundraiser',
                    goal=100,
                    photo=self._make_image_upload(100, 60),
                )
                self.assertTrue(fundraiser.photo_small.name)
                thumb = os.path.join(settings.MEDIA_ROOT, fundraiser.photo_small.name)
                with Image.open(thumb) as img:
                    self.assertEqual(img.size, (100, 60))

    def test_replacing_photo_refreshes_thumbnail(self):
        """
        Replacing the photo regenerates photo_small from the new image rather
        than leaving the previous thumbnail in place.
        """
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                fundraiser = Fundraiser.objects.create(
                    campaign=self.campaign,
                    name='Photo Fundraiser',
                    goal=100,
                    photo=self._make_image_upload(100, 60, color=(255, 0, 0)),
                )

                # Replace with a differently sized, differently coloured image.
                fundraiser.photo = self._make_image_upload(80, 80, color=(0, 255, 0))
                fundraiser.save()

                thumb = os.path.join(settings.MEDIA_ROOT, fundraiser.photo_small.name)
                with Image.open(thumb) as img:
                    self.assertEqual(img.size, (80, 80))
                    self.assertEqual(img.convert('RGB').getpixel((0, 0)), (0, 255, 0))

    def test_rotate_photo_ignores_invalid_degrees(self):
        """ A non-90-multiple rotation is a no-op and leaves the photo intact """
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                fundraiser = Fundraiser.objects.create(
                    campaign=self.campaign,
                    name='Photo Fundraiser',
                    goal=100,
                    photo=self._make_image_upload(100, 60),
                )
                path = os.path.join(settings.MEDIA_ROOT, fundraiser.photo.name)

                fundraiser.rotate_photo(45)

                with Image.open(path) as img:
                    self.assertEqual(img.size, (100, 60))


class TestDonation(TestModels):

    def test_name(self):
        """ Check the donation .__str__ function """
        donation = Donation.objects.first()
        self.assertEqual(str(donation), 'First Donator')


class TestDonorManager(TestModels):

    def test_donor_total_donations(self):
        """
        Check that donations from the same donor (name, email)
        are summed together
        """
        donors = Donor.objects.all()
        donations = donors[0]['amount']
        self.assertEqual(donations, 83.00)
