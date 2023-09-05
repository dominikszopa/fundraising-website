from django.test import TestCase
from django.utils import timezone
from ..models import Campaign, Fundraiser, Donation, Donor


class TestModels(TestCase):
    """ Parent class that builds all data for base model tests """

    @classmethod
    def setUpTestData(cls):
        Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='message',
            default_fundraiser_message='default message',
        )

        campaign1 = Campaign.objects.get(id=1)

        # A fundraiser with a few donations already
        Fundraiser.objects.create(
            campaign=campaign1,
            name='First Fundraiser',
            goal=200,
            photo='',
            message='You go dude!',
        )

        fundraiser1 = Fundraiser.objects.get(id=1)

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
        campaign = Campaign.objects.get(id=1)
        self.assertEquals(str(campaign), 'Test Campaign')

    def test_donation_total(self):
        """ Verify total donations sum is correct """
        campaign = Campaign.objects.get(id=1)
        total = campaign.get_total_raised()
        self.assertEquals(total, 83.00)


class TestFundraiser(TestModels):

    def test_name(self):
        """ Check the Fundraiser .__str__ function """
        fundraiser = Fundraiser.objects.get(id=1)
        self.assertEquals(str(fundraiser), 'First Fundraiser')

    def test_donation_total(self):
        """ Verify total donations for fundraiser is correct """
        fundraiser = Fundraiser.objects.get(id=1)
        total = fundraiser.total_raised()
        self.assertEquals(total, 83.00)

    def test_total_donators(self):
        """ Check the number of donators is correct """
        fundraiser = Fundraiser.objects.get(id=1)
        total = fundraiser.total_donations()
        self.assertEquals(total, 2)


class TestDonation(TestModels):

    def test_name(self):
        """ Check the donation .__str__ function """
        donation = Donation.objects.get(id=1)
        self.assertEquals(str(donation), 'First Donator')


class TestDonorManager(TestModels):

    def test_donor_total_donations(self):
        """
        Check that donations from the same donor (name, email)
        are summed together
        """
        donors = Donor.objects.all()
        donations = donors[0]['amount']
        self.assertEquals(donations, 83.00)
