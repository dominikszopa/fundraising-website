from django.test import TestCase
from ..models import Campaign


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


class TestCampaignModel(TestModels):

    def test_name(self):
        """ Check the Campaign.__str__ function """
        campaign = Campaign.objects.get(id=1)
        self.assertEquals(str(campaign), 'first')
