from django.test import TestCase
from ..models import Campaign


class TestModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.campaign = Campaign.objects.create(
            name='first',
            goal=1000,
            campaign_message='message',
            default_fundraiser_message='default message',
        )

    def test_name(self):
        """Check the Campaign.__str__ function"""

        self.assertEquals(str(self.campaign), 'first')
