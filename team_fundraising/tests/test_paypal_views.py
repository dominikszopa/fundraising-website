"""Tests for the Advanced Checkout views (create/capture/webhook).

PayPal HTTP calls and email sends are mocked; we're testing view behavior,
state transitions, and idempotency — not the real PayPal sandbox.
"""
import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import Campaign, Donation, Fundraiser


@override_settings(
    PAYPAL_CLIENT_ID='test-client-id',
    PAYPAL_CLIENT_SECRET='test-secret',
    PAYPAL_API_BASE='https://api-m.sandbox.paypal.com',
    PAYPAL_WEBHOOK_ID='WH-TEST',
)
class PayPalViewsTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.campaign = Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='Test',
            default_fundraiser_message='Default',
            default_fundraiser_amount=100,
        )
        cls.fundraiser = Fundraiser.objects.create(
            campaign=cls.campaign, name='Test Fundraiser', goal=500,
        )


class TestCreateDonationOrder(PayPalViewsTestBase):

    def _valid_form_data(self, amount='50.00'):
        return {
            'name': 'Jane Donor',
            'email': 'jane@example.com',
            'amount': amount,
            'anonymous': False,
            'message': 'Go!',
            'tax_name': '',
            'address': '',
            'city': '',
            'province': '',
            'country': '',
            'postal_code': '',
        }

    @patch('team_fundraising.views.paypal_api.create_order')
    def test_creates_pending_donation_and_returns_order_id(self, mock_create):
        mock_create.return_value = {'id': 'ORDER-ABC', 'status': 'CREATED'}

        response = self.client.post(
            reverse(
                'team_fundraising:create_order',
                args=[self.fundraiser.id],
            ),
            data=self._valid_form_data(),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['orderID'], 'ORDER-ABC')

        donation = Donation.objects.get(pk=body['donationID'])
        self.assertEqual(donation.payment_status, 'pending')
        self.assertEqual(donation.amount, 50.0)
        self.assertEqual(donation.fundraiser, self.fundraiser)
        mock_create.assert_called_once()

    @patch('team_fundraising.views.paypal_api.create_order')
    def test_accepts_json_body(self, mock_create):
        mock_create.return_value = {'id': 'ORDER-JSON'}

        response = self.client.post(
            reverse(
                'team_fundraising:create_order',
                args=[self.fundraiser.id],
            ),
            data=json.dumps(self._valid_form_data()),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['orderID'], 'ORDER-JSON')

    @patch('team_fundraising.views.paypal_api.create_order')
    def test_rejects_invalid_form(self, mock_create):
        response = self.client.post(
            reverse(
                'team_fundraising:create_order',
                args=[self.fundraiser.id],
            ),
            data={'name': 'Jane'},  # missing email, amount
        )
        self.assertEqual(response.status_code, 400)
        mock_create.assert_not_called()
        self.assertEqual(Donation.objects.count(), 0)

    @patch('team_fundraising.views.paypal_api.create_order')
    def test_returns_502_on_paypal_error(self, mock_create):
        from .. import paypal_api
        mock_create.side_effect = paypal_api.PayPalAPIError('boom')

        response = self.client.post(
            reverse(
                'team_fundraising:create_order',
                args=[self.fundraiser.id],
            ),
            data=self._valid_form_data(),
        )

        self.assertEqual(response.status_code, 502)
        # Donation row still exists — we keep pending records for debugging.
        self.assertEqual(Donation.objects.count(), 1)


class TestCaptureDonationOrder(PayPalViewsTestBase):

    def setUp(self):
        self.donation = Donation.objects.create(
            fundraiser=self.fundraiser,
            name='Jane', email='jane@example.com',
            amount=50.0, message='',
            payment_method='paypal', payment_status='pending',
        )

    def _capture_payload(self, amount='50.00', currency='CAD', status='COMPLETED'):
        return {
            'id': 'ORDER-1',
            'status': status,
            'purchase_units': [{
                'payments': {'captures': [{
                    'amount': {'value': amount, 'currency_code': currency},
                }]},
            }],
        }

    @patch('team_fundraising.views.send_donation_emails')
    @patch('team_fundraising.views.paypal_api.capture_order')
    def test_marks_paid_and_sends_emails(self, mock_capture, mock_emails):
        mock_capture.return_value = self._capture_payload()

        response = self.client.post(
            reverse('team_fundraising:capture_order', args=[self.donation.id]),
            data=json.dumps({'orderID': 'ORDER-1'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.payment_status, 'paid')
        mock_emails.assert_called_once()

    @patch('team_fundraising.views.send_donation_emails')
    @patch('team_fundraising.views.paypal_api.capture_order')
    def test_second_capture_does_not_resend_emails(self, mock_capture, mock_emails):
        mock_capture.return_value = self._capture_payload()
        url = reverse('team_fundraising:capture_order', args=[self.donation.id])
        body = json.dumps({'orderID': 'ORDER-1'})

        self.client.post(url, data=body, content_type='application/json')
        self.client.post(url, data=body, content_type='application/json')

        self.assertEqual(mock_emails.call_count, 1)

    @patch('team_fundraising.views.send_donation_emails')
    @patch('team_fundraising.views.paypal_api.capture_order')
    def test_rejects_amount_mismatch(self, mock_capture, mock_emails):
        mock_capture.return_value = self._capture_payload(amount='10.00')

        response = self.client.post(
            reverse('team_fundraising:capture_order', args=[self.donation.id]),
            data=json.dumps({'orderID': 'ORDER-1'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.payment_status, 'pending')
        mock_emails.assert_not_called()

    @patch('team_fundraising.views.paypal_api.capture_order')
    def test_rejects_non_completed_status(self, mock_capture):
        mock_capture.return_value = self._capture_payload(status='PENDING')

        response = self.client.post(
            reverse('team_fundraising:capture_order', args=[self.donation.id]),
            data=json.dumps({'orderID': 'ORDER-1'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_missing_order_id(self):
        response = self.client.post(
            reverse('team_fundraising:capture_order', args=[self.donation.id]),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class TestPayPalWebhook(PayPalViewsTestBase):

    def setUp(self):
        self.donation = Donation.objects.create(
            fundraiser=self.fundraiser,
            name='Jane', email='jane@example.com',
            amount=50.0, message='',
            payment_method='paypal', payment_status='pending',
        )

    def _event(self, event_type='PAYMENT.CAPTURE.COMPLETED', custom_id=None):
        return {
            'event_type': event_type,
            'resource': {
                'custom_id': str(custom_id or self.donation.id),
                'status': 'COMPLETED',
            },
        }

    @patch('team_fundraising.views.send_donation_emails')
    @patch('team_fundraising.views.paypal_api.verify_webhook')
    def test_marks_paid_on_verified_completion(self, mock_verify, mock_emails):
        mock_verify.return_value = True
        body = json.dumps(self._event()).encode()

        response = self.client.post(
            reverse('team_fundraising:paypal_webhook'),
            data=body,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.payment_status, 'paid')
        mock_emails.assert_called_once()

    @patch('team_fundraising.views.send_donation_emails')
    @patch('team_fundraising.views.paypal_api.verify_webhook')
    def test_already_paid_does_not_resend(self, mock_verify, mock_emails):
        mock_verify.return_value = True
        self.donation.payment_status = 'paid'
        self.donation.save()

        response = self.client.post(
            reverse('team_fundraising:paypal_webhook'),
            data=json.dumps(self._event()).encode(),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        mock_emails.assert_not_called()

    @patch('team_fundraising.views.paypal_api.verify_webhook')
    def test_rejects_bad_signature(self, mock_verify):
        mock_verify.return_value = False

        response = self.client.post(
            reverse('team_fundraising:paypal_webhook'),
            data=json.dumps(self._event()).encode(),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.payment_status, 'pending')

    @patch('team_fundraising.views.send_donation_emails')
    @patch('team_fundraising.views.paypal_api.verify_webhook')
    def test_non_completion_event_does_nothing(self, mock_verify, mock_emails):
        mock_verify.return_value = True

        response = self.client.post(
            reverse('team_fundraising:paypal_webhook'),
            data=json.dumps(self._event(
                event_type='PAYMENT.CAPTURE.REFUNDED',
            )).encode(),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.payment_status, 'pending')
        mock_emails.assert_not_called()

    @patch('team_fundraising.views.paypal_api.verify_webhook')
    def test_unknown_donation_returns_404(self, mock_verify):
        mock_verify.return_value = True

        response = self.client.post(
            reverse('team_fundraising:paypal_webhook'),
            data=json.dumps(self._event(custom_id=99999)).encode(),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)


@override_settings(PAYPAL_CLIENT_ID='test-client-id')
class TestDonationTemplateFeatureFlag(PayPalViewsTestBase):
    """Ensures the feature flag picks the right template."""

    @override_settings(PAYPAL_ADVANCED_CHECKOUT=False)
    def test_legacy_template_when_flag_off(self):
        response = self.client.get(
            reverse('team_fundraising:donation', args=[self.fundraiser.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_fundraising/donation.html')

    @override_settings(PAYPAL_ADVANCED_CHECKOUT=True)
    def test_advanced_template_when_flag_on(self):
        response = self.client.get(
            reverse('team_fundraising:donation', args=[self.fundraiser.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'team_fundraising/donation_advanced.html',
        )
        # Sanity: client id and SDK script are in the rendered page.
        self.assertContains(response, 'paypal.com/sdk/js')
        self.assertContains(response, 'test-client-id')
