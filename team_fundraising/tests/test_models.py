from django.test import TestCase
from ..models import Campaign, Fundraiser, Donation


class TestModels(TestCase):
    """ Parent class that builds all data for base model tests """

    @classmethod
    def setUpTestData(cls):
        Campaign.objects.create(
            name='first',
            goal=1000,
            campaign_message='message',
            default_fundraiser_message='default message',
        )

        campaign1 = Campaign.objects.get(id=1)

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
            name='First Donation',
            amount='50.00',
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
        )

        Donation.objects.create(
            fundraiser=fundraiser1,
            name='Second Donation',
            amount='33.00',
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
        )


class TestCampaignModel(TestModels):

    def test_name(self):
        """ Check the Campaign.__str__ function """
        campaign = Campaign.objects.get(id=1)
        self.assertEquals(str(campaign), 'first')

    def test_donation_total(self):
        campaign = Campaign.objects.get(id=1)
        total = campaign.total_raised()
        self.assertEquals(total, 83.00)
