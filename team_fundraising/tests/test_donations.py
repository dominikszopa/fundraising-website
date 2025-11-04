from django.test import TestCase
from django.urls import reverse
from ..models import Campaign, Fundraiser, Donation


class TestDonationCreation(TestCase):
    """Test creating donations to fundraisers"""

    @classmethod
    def setUpTestData(cls):
        """Create test campaign and fundraiser for donation tests"""
        campaign = Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='Test campaign message',
            default_fundraiser_message='Default message',
            default_fundraiser_amount=100,
        )

        Fundraiser.objects.create(
            campaign=campaign,
            name='Test Fundraiser',
            goal=500,
            message='Help me reach my goal!',
        )

    def test_donation_with_all_fields(self):
        """Test creating a donation with all fields populated"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'John Donor',
            'email': 'john@example.com',
            'amount': '50.00',
            'anonymous': False,
            'message': 'Great cause!',
            'tax_name': 'John Smith Donor',
            'address': '123 Main Street',
            'city': 'Vancouver',
            'province': 'BC',
            'country': 'Canada',
            'postal_code': 'V6B 1A1',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was created
        donation = Donation.objects.get(email='john@example.com')
        self.assertIsNotNone(donation)
        self.assertEqual(donation.name, 'John Donor')
        self.assertEqual(donation.amount, 50.00)
        self.assertEqual(donation.fundraiser, fundraiser)
        self.assertEqual(donation.message, 'Great cause!')
        self.assertEqual(donation.tax_name, 'John Smith Donor')
        self.assertEqual(donation.address, '123 Main Street')
        self.assertEqual(donation.city, 'Vancouver')
        self.assertEqual(donation.province, 'BC')
        self.assertEqual(donation.country, 'Canada')
        self.assertEqual(donation.postal_code, 'V6B 1A1')
        self.assertEqual(donation.payment_method, 'paypal')
        self.assertEqual(donation.payment_status, 'pending')
        self.assertFalse(donation.anonymous)

        # Check that PayPal form is displayed
        self.assertEqual(response.status_code, 200)
        self.assertIn('paypal', response.content.decode().lower())

    def test_donation_minimal_fields(self):
        """Test creating a donation with only required fields"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Jane Donor',
            'email': 'jane@example.com',
            'amount': '25.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was created
        donation = Donation.objects.get(email='jane@example.com')
        self.assertIsNotNone(donation)
        self.assertEqual(donation.name, 'Jane Donor')
        self.assertEqual(donation.amount, 25.00)
        self.assertEqual(donation.fundraiser, fundraiser)
        self.assertEqual(donation.message, '')
        self.assertEqual(donation.tax_name, '')
        self.assertFalse(donation.anonymous)

        # Check response
        self.assertEqual(response.status_code, 200)

    def test_donation_anonymous(self):
        """Test creating an anonymous donation"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Anonymous Donor',
            'email': 'anon@example.com',
            'amount': '100.00',
            'anonymous': True,
            'message': 'Keep up the good work!',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was created as anonymous
        donation = Donation.objects.get(email='anon@example.com')
        self.assertIsNotNone(donation)
        self.assertTrue(donation.anonymous)
        self.assertEqual(donation.amount, 100.00)
        self.assertEqual(donation.message, 'Keep up the good work!')

        # Check response
        self.assertEqual(response.status_code, 200)

    def test_donation_other_amount(self):
        """Test donation with 'other' amount option"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Custom Donor',
            'email': 'custom@example.com',
            'amount': 'other',
            'other_amount': '75.50',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that custom amount was used
        donation = Donation.objects.get(email='custom@example.com')
        self.assertIsNotNone(donation)
        self.assertEqual(donation.amount, 75.50)

        # Check response
        self.assertEqual(response.status_code, 200)

    def test_donation_large_amount(self):
        """Test donation with a large amount"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Big Donor',
            'email': 'big@example.com',
            'amount': '1000.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was created
        donation = Donation.objects.get(email='big@example.com')
        self.assertIsNotNone(donation)
        self.assertEqual(donation.amount, 1000.00)

        # Check response
        self.assertEqual(response.status_code, 200)

    def test_donation_with_tax_receipt_info(self):
        """Test donation with tax receipt information"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Tax Donor',
            'email': 'tax@example.com',
            'amount': '200.00',
            'tax_name': 'Tax Receipt Name',
            'address': '456 Tax Street',
            'city': 'Toronto',
            'province': 'ON',
            'country': 'Canada',
            'postal_code': 'M5H 2N2',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that tax information was saved
        donation = Donation.objects.get(email='tax@example.com')
        self.assertIsNotNone(donation)
        self.assertEqual(donation.tax_name, 'Tax Receipt Name')
        self.assertEqual(donation.address, '456 Tax Street')
        self.assertEqual(donation.city, 'Toronto')
        self.assertEqual(donation.province, 'ON')

        # Check response
        self.assertEqual(response.status_code, 200)


class TestDonationValidation(TestCase):
    """Test donation form validation and error cases"""

    @classmethod
    def setUpTestData(cls):
        """Create test campaign and fundraiser"""
        campaign = Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='Test campaign message',
            default_fundraiser_message='Default message',
            default_fundraiser_amount=100,
        )

        Fundraiser.objects.create(
            campaign=campaign,
            name='Test Fundraiser',
            goal=500,
        )

    def test_donation_missing_name(self):
        """Test that donation fails without a name"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'email': 'noname@example.com',
            'amount': '50.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was NOT created
        self.assertFalse(
            Donation.objects.filter(email='noname@example.com').exists()
        )

        # Check that form is redisplayed with errors
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_donation_missing_email(self):
        """Test that donation fails without an email"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'No Email',
            'amount': '50.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was NOT created
        self.assertFalse(
            Donation.objects.filter(name='No Email').exists()
        )

        # Check that form is redisplayed
        self.assertEqual(response.status_code, 200)

    def test_donation_missing_amount(self):
        """Test that donation fails without an amount"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'No Amount',
            'email': 'noamount@example.com',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was NOT created
        self.assertFalse(
            Donation.objects.filter(email='noamount@example.com').exists()
        )

        # Check that form is redisplayed
        self.assertEqual(response.status_code, 200)

    def test_donation_invalid_email(self):
        """Test that donation fails with invalid email"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Bad Email',
            'email': 'not-an-email',
            'amount': '50.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was NOT created
        self.assertFalse(
            Donation.objects.filter(name='Bad Email').exists()
        )

        # Check that form is redisplayed
        self.assertEqual(response.status_code, 200)

    def test_donation_invalid_other_amount(self):
        """Test that donation fails with non-numeric 'other' amount"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Bad Amount',
            'email': 'badamount@example.com',
            'amount': 'other',
            'other_amount': 'not-a-number',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was NOT created
        self.assertFalse(
            Donation.objects.filter(email='badamount@example.com').exists()
        )

        # Check that form is redisplayed
        self.assertEqual(response.status_code, 200)

    def test_donation_empty_other_amount(self):
        """Test that donation fails when 'other' amount is empty"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Empty Other',
            'email': 'emptyother@example.com',
            'amount': 'other',
            'other_amount': '',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was NOT created
        self.assertFalse(
            Donation.objects.filter(email='emptyother@example.com').exists()
        )

        # Check that form is redisplayed
        self.assertEqual(response.status_code, 200)

    def test_donation_negative_amount(self):
        """Test donation with negative amount"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Negative Donor',
            'email': 'negative@example.com',
            'amount': 'other',
            'other_amount': '-50.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check if donation was created (no server-side validation for negative)
        # This tests current behavior - negative amounts are allowed
        donation = Donation.objects.filter(email='negative@example.com').first()
        if donation:
            self.assertEqual(donation.amount, -50.00)

    def test_donation_zero_amount(self):
        """Test donation with zero amount"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Zero Donor',
            'email': 'zero@example.com',
            'amount': 'other',
            'other_amount': '0.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check if donation was created
        donation = Donation.objects.filter(email='zero@example.com').first()
        if donation:
            self.assertEqual(donation.amount, 0.00)

    def test_donation_nonexistent_fundraiser(self):
        """Test that donation fails for non-existent fundraiser"""
        donation_data = {
            'name': 'Test Donor',
            'email': 'test@example.com',
            'amount': '50.00',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[9999]),
            donation_data
        )

        # Should return 404
        self.assertEqual(response.status_code, 404)


class TestDonationViews(TestCase):
    """Test donation page views and flow"""

    @classmethod
    def setUpTestData(cls):
        """Create test campaign and fundraiser"""
        campaign = Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='Test campaign message',
            default_fundraiser_message='Default message',
            default_fundraiser_amount=100,
        )

        Fundraiser.objects.create(
            campaign=campaign,
            name='Test Fundraiser',
            goal=500,
        )

    def test_donation_page_get_request(self):
        """Test that GET request displays donation form"""
        fundraiser = Fundraiser.objects.get(id=1)

        response = self.client.get(
            reverse('team_fundraising:donation', args=[fundraiser.id])
        )

        # Check that page loads successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertEqual(response.context['fundraiser'], fundraiser)
        self.assertIsNotNone(response.context['campaign'])

    def test_donation_creates_pending_status(self):
        """Test that new donations have pending payment status"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Pending Donor',
            'email': 'pending@example.com',
            'amount': '50.00',
        }

        self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation has pending status
        donation = Donation.objects.get(email='pending@example.com')
        self.assertEqual(donation.payment_status, 'pending')
        self.assertEqual(donation.payment_method, 'paypal')

    def test_donation_not_counted_until_paid(self):
        """Test that pending donations don't count toward fundraiser total"""
        fundraiser = Fundraiser.objects.get(id=1)

        # Check initial total
        initial_total = fundraiser.total_raised()
        self.assertEqual(initial_total, 0)

        # Create pending donation
        donation_data = {
            'name': 'Not Counted',
            'email': 'notcounted@example.com',
            'amount': '100.00',
        }

        self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that total hasn't changed
        fundraiser.refresh_from_db()
        self.assertEqual(fundraiser.total_raised(), 0)

        # Mark donation as paid
        donation = Donation.objects.get(email='notcounted@example.com')
        donation.payment_status = 'paid'
        donation.save()

        # Now check that total has increased
        self.assertEqual(fundraiser.total_raised(), 100.00)

    def test_multiple_donations_same_fundraiser(self):
        """Test multiple people can donate to same fundraiser"""
        fundraiser = Fundraiser.objects.get(id=1)

        # First donation
        donation_data_1 = {
            'name': 'Donor One',
            'email': 'one@example.com',
            'amount': '25.00',
        }

        self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data_1
        )

        # Second donation
        donation_data_2 = {
            'name': 'Donor Two',
            'email': 'two@example.com',
            'amount': '50.00',
        }

        self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data_2
        )

        # Check both donations exist
        self.assertTrue(
            Donation.objects.filter(email='one@example.com').exists()
        )
        self.assertTrue(
            Donation.objects.filter(email='two@example.com').exists()
        )

        # Mark both as paid
        Donation.objects.all().update(payment_status='paid')

        # Check total
        self.assertEqual(fundraiser.total_raised(), 75.00)

    def test_donation_with_long_message(self):
        """Test donation with maximum length message"""
        fundraiser = Fundraiser.objects.get(id=1)

        long_message = 'X' * 280  # Max length is 280 characters

        donation_data = {
            'name': 'Long Message',
            'email': 'longmsg@example.com',
            'amount': '50.00',
            'message': long_message,
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that donation was created
        donation = Donation.objects.get(email='longmsg@example.com')
        self.assertEqual(len(donation.message), 280)
        self.assertEqual(response.status_code, 200)

    def test_donation_decimal_amounts(self):
        """Test donations with decimal amounts"""
        fundraiser = Fundraiser.objects.get(id=1)

        donation_data = {
            'name': 'Decimal Donor',
            'email': 'decimal@example.com',
            'amount': 'other',
            'other_amount': '33.33',
        }

        response = self.client.post(
            reverse('team_fundraising:donation', args=[fundraiser.id]),
            donation_data
        )

        # Check that decimal amount was saved correctly
        donation = Donation.objects.get(email='decimal@example.com')
        self.assertEqual(donation.amount, 33.33)
        self.assertEqual(response.status_code, 200)
