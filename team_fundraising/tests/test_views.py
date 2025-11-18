from .test_models import TestModels
from django.urls import reverse
from ..models import Campaign, Fundraiser


class HomePageViewTests(TestModels):
    """ Test homepage information based on TestModels data """

    def test_homepage_loads(self):
        # Just test the top of the homepage loads with the campaign name
        campaign = Campaign.objects.get(name='Test Campaign')
        response = self.client.get(reverse('team_fundraising:index', args=[campaign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['campaign'].name, 'Test Campaign')

    def test_homepage_totals(self):
        # Check the homepage displays total donations and raised
        campaign = Campaign.objects.get(name='Test Campaign')
        response = self.client.get(reverse('team_fundraising:index', args=[campaign.id]))
        self.assertEqual(response.context['total_raised'], 83.00)
        self.assertEqual(response.context['campaign'].goal, 1000.00)

    def test_homepage_fundraiser(self):
        # Check the first fundraiser has the right information
        campaign = Campaign.objects.get(name='Test Campaign')
        response = self.client.get(reverse('team_fundraising:index', args=[campaign.id]))
        self.assertEqual(
            response.context['fundraisers'][0].name, 'First Fundraiser'
        )
        self.assertEqual(
            response.context['fundraisers'][0].total_raised, 83.00
        )
        self.assertEqual(
            response.context['fundraisers'][0].goal, 200.00
        )

    def test_empty_homepage_fundraiser(self):
        # Check a fundraiser without donations still shows up
        campaign = Campaign.objects.get(name='Test Campaign')
        response = self.client.get(reverse('team_fundraising:index', args=[campaign.id]))
        self.assertEqual(
            response.context['fundraisers'][1].name, 'Empty Fundraiser'
        )
        self.assertEqual(
            response.context['fundraisers'][1].total_raised, 00.00
        )
        self.assertEqual(
            response.context['fundraisers'][1].goal, 100.00
        )

    def test_recent_donations(self):
        campaign = Campaign.objects.get(name='Test Campaign')
        response = self.client.get(reverse('team_fundraising:index', args=[campaign.id]))
        self.assertEqual(
            response.context['recent_donations'][0].amount, 33.00
        )


class FundraiserViewTests(TestModels):
    """ Check the information on the fundraiser page """

    def test_fundraiser(self):
        """ Check the information on the first fundraiser """
        fundraiser = Fundraiser.objects.get(name='First Fundraiser')
        response = self.client.get(
            reverse('team_fundraising:fundraiser', args=[fundraiser.id])
        )
        self.assertEqual(
            response.context['fundraiser'].name, 'First Fundraiser'
        )
        self.assertEqual(
            response.context['fundraiser'].goal, 200.00
        )
        self.assertEqual(
            response.context['fundraiser'].total_raised, 83.00
        )
        self.assertEqual(
            response.context['fundraiser'].percent_raised, 83/200*100
        )

    def test_empty_fundraiser(self):
        """ Check the information on a fundraiser without donations """
        fundraiser = Fundraiser.objects.get(name='Empty Fundraiser')
        response = self.client.get(
            reverse('team_fundraising:fundraiser', args=[fundraiser.id])
        )
        self.assertEqual(
            response.context['fundraiser'].name, 'Empty Fundraiser'
        )
        self.assertEqual(
            response.context['fundraiser'].goal, 100.00
        )
        self.assertEqual(
            response.context['fundraiser'].total_raised, 0.00
        )
        self.assertEqual(
            response.context['fundraiser'].percent_raised, 0.00
        )
