from django.test import TestCase
from django.urls import reverse


class GeneralTests(TestCase):

    fixtures = ['testdata.json']

    def test_homepage_loads(self):
        # Just test the top of the homepage loads
        response = self.client.get(reverse('team_fundraising:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home')
