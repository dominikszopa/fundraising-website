from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Campaign, Fundraiser


class TestFundraiserSignup(TestCase):
    """Test creating new fundraiser accounts"""

    @classmethod
    def setUpTestData(cls):
        """Create a test campaign for signup tests"""
        Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='Test campaign message',
            default_fundraiser_message='Default message',
            default_fundraiser_amount=100,
        )

    def test_signup_new_user_and_fundraiser(self):
        """Test creating a new user and fundraiser together"""
        campaign = Campaign.objects.first()

        signup_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'campaign': campaign.id,
            'name': 'Test Fundraiser',
            'team': 'Test Team',
            'goal': 200,
            'message': 'My fundraising message',
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Check that user was created
        user = User.objects.get(username='testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

        # Check that fundraiser was created
        fundraiser = Fundraiser.objects.get(name='Test Fundraiser')
        self.assertIsNotNone(fundraiser)
        self.assertEqual(fundraiser.user, user)
        self.assertEqual(fundraiser.campaign, campaign)
        self.assertEqual(fundraiser.team, 'Test Team')
        self.assertEqual(fundraiser.goal, 200)
        self.assertEqual(fundraiser.message, 'My fundraising message')

        # Check that user is redirected
        self.assertEqual(response.status_code, 302)

    def test_signup_minimal_required_fields(self):
        """Test creating fundraiser with only required fields"""
        campaign = Campaign.objects.first()

        signup_data = {
            'username': 'minimaluser',
            'email': 'minimal@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'campaign': campaign.id,
            'name': 'Minimal Fundraiser',
            'goal': 100,
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Check that user and fundraiser were created
        user = User.objects.get(username='minimaluser')
        self.assertIsNotNone(user)

        fundraiser = Fundraiser.objects.get(name='Minimal Fundraiser')
        self.assertIsNotNone(fundraiser)
        self.assertEqual(fundraiser.user, user)
        self.assertEqual(fundraiser.team, '')
        self.assertEqual(fundraiser.message, '')

    def test_signup_existing_user_new_fundraiser(self):
        """Test adding a new fundraiser to an existing user account"""
        campaign = Campaign.objects.first()

        # Create an existing user
        existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='oldpass123'
        )

        signup_data = {
            'username': 'existinguser',
            'password1': 'oldpass123',
            'password2': 'oldpass123',
            'campaign': campaign.id,
            'name': 'Second Fundraiser',
            'team': 'Team B',
            'goal': 300,
            'message': 'Another fundraiser',
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Check that no new user was created
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

        # Check that fundraiser was created for existing user
        fundraiser = Fundraiser.objects.get(name='Second Fundraiser')
        self.assertIsNotNone(fundraiser)
        self.assertEqual(fundraiser.user, existing_user)
        self.assertEqual(fundraiser.goal, 300)

    def test_signup_existing_user_wrong_password(self):
        """Test that signup fails with wrong password for existing user"""
        campaign = Campaign.objects.first()

        # Create an existing user
        User.objects.create_user(
            username='existinguser2',
            email='existing2@example.com',
            password='correctpass123'
        )

        signup_data = {
            'username': 'existinguser2',
            'password1': 'wrongpass123',
            'password2': 'wrongpass123',
            'campaign': campaign.id,
            'name': 'Should Not Be Created',
            'goal': 100,
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Check that fundraiser was NOT created
        self.assertFalse(
            Fundraiser.objects.filter(name='Should Not Be Created').exists()
        )

        # Check error message was shown
        self.assertEqual(response.status_code, 200)

    def test_signup_duplicate_fundraiser_in_same_campaign(self):
        """Test that user cannot create duplicate fundraiser in same campaign"""
        campaign = Campaign.objects.first()

        # Create user with existing fundraiser
        user = User.objects.create_user(
            username='duplicateuser',
            email='duplicate@example.com',
            password='testpass123'
        )
        Fundraiser.objects.create(
            campaign=campaign,
            user=user,
            name='First Fundraiser',
            goal=100,
        )

        signup_data = {
            'username': 'duplicateuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'campaign': campaign.id,
            'name': 'Duplicate Fundraiser',
            'goal': 200,
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Should redirect to update fundraiser page
        self.assertEqual(response.status_code, 302)
        self.assertTrue('update' in response.url)

        # Check that duplicate fundraiser was NOT created
        self.assertEqual(Fundraiser.objects.filter(user=user).count(), 1)

    def test_signup_authenticated_user_adding_fundraiser(self):
        """Test that already logged-in user can add a fundraiser"""
        campaign = Campaign.objects.first()

        # Create and log in a user
        user = User.objects.create_user(
            username='loggedinuser',
            email='loggedin@example.com',
            password='testpass123'
        )
        self.client.login(username='loggedinuser', password='testpass123')

        signup_data = {
            'username': 'loggedinuser',
            'campaign': campaign.id,
            'name': 'Authenticated User Fundraiser',
            'goal': 250,
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Check that fundraiser was created
        fundraiser = Fundraiser.objects.get(name='Authenticated User Fundraiser')
        self.assertIsNotNone(fundraiser)
        self.assertEqual(fundraiser.user, user)

    def test_signup_missing_fundraiser_name(self):
        """Test that signup fails when fundraiser name is missing"""
        campaign = Campaign.objects.first()

        # Missing fundraiser name
        signup_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'campaign': campaign.id,
            'goal': 100,
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Check that form was invalid and no user was created
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

    def test_signup_missing_goal(self):
        """Test that signup fails when required fundraiser field is missing"""
        campaign = Campaign.objects.first()

        signup_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'campaign': campaign.id,
            'name': 'Test Fundraiser',
            # Missing required 'goal' field
        }

        response = self.client.post(
            reverse('team_fundraising:signup', args=[campaign.id]),
            signup_data
        )

        # Check that response shows form errors
        self.assertEqual(response.status_code, 200)
        # User might be created but fundraiser should not be
        self.assertFalse(
            Fundraiser.objects.filter(name='Test Fundraiser').exists()
        )

    def test_signup_get_request(self):
        """Test that GET request displays signup form"""
        campaign = Campaign.objects.first()

        response = self.client.get(
            reverse('team_fundraising:signup', args=[campaign.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('user_form', response.context)
        self.assertIn('fundraiser_form', response.context)
        self.assertEqual(response.context['campaign'], campaign)

    def test_signup_prepopulates_for_authenticated_user(self):
        """Test that signup form prepopulates data for logged-in users"""
        campaign = Campaign.objects.first()

        # Create and log in a user
        user = User.objects.create_user(
            username='existinglogged',
            email='existinglogged@example.com',
            password='testpass123'
        )
        self.client.login(username='existinglogged', password='testpass123')

        response = self.client.get(
            reverse('team_fundraising:signup', args=[campaign.id])
        )

        # Check that form is prepopulated with user data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['user_form'].initial['username'],
            'existinglogged'
        )
        self.assertEqual(
            response.context['user_form'].initial['email'],
            'existinglogged@example.com'
        )


class TestOneClickSignup(TestCase):
    """Test one-click signup for existing users in new campaigns"""

    @classmethod
    def setUpTestData(cls):
        """Create test campaigns and user with fundraiser"""
        Campaign.objects.create(
            name='Campaign 2024',
            goal=1000,
            campaign_message='2024 campaign',
            default_fundraiser_message='Default message',
            default_fundraiser_amount=100,
        )
        Campaign.objects.create(
            name='Campaign 2025',
            goal=1500,
            campaign_message='2025 campaign',
            default_fundraiser_message='Default message',
            default_fundraiser_amount=150,
        )

    def test_one_click_signup_creates_new_fundraiser(self):
        """Test that one-click signup creates a new fundraiser from previous"""
        campaign_2024 = Campaign.objects.get(name='Campaign 2024')
        campaign_2025 = Campaign.objects.get(name='Campaign 2025')

        # Create user with existing fundraiser
        user = User.objects.create_user(
            username='returninguser',
            email='returning@example.com',
            password='testpass123'
        )
        old_fundraiser = Fundraiser.objects.create(
            campaign=campaign_2024,
            user=user,
            name='My Name 2024',
            team='Team Alpha',
            goal=100,
            message='My 2024 message',
        )

        # Log in and do one-click signup
        self.client.login(username='returninguser', password='testpass123')
        response = self.client.get(
            reverse('team_fundraising:signup_logged_in', args=[campaign_2025.id])
        )

        # Check that new fundraiser was created
        new_fundraiser = Fundraiser.objects.get(campaign=campaign_2025, user=user)
        self.assertIsNotNone(new_fundraiser)
        self.assertEqual(new_fundraiser.name, old_fundraiser.name)
        self.assertEqual(new_fundraiser.team, old_fundraiser.team)
        self.assertEqual(new_fundraiser.message, old_fundraiser.message)
        self.assertEqual(new_fundraiser.goal, campaign_2025.default_fundraiser_amount)

        # Check redirect to update page
        self.assertEqual(response.status_code, 302)
        self.assertTrue('update' in response.url)

    def test_one_click_signup_requires_authentication(self):
        """Test that one-click signup requires user to be logged in"""
        campaign_2025 = Campaign.objects.get(name='Campaign 2025')

        response = self.client.get(
            reverse('team_fundraising:signup_logged_in', args=[campaign_2025.id])
        )

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue('login' in response.url)
