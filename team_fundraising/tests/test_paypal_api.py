"""Unit tests for the PayPal REST client (team_fundraising/paypal_api.py).

HTTP calls are mocked; these tests check request shape and response handling
only. They do not exercise the real PayPal sandbox.
"""
import json
from unittest.mock import patch, MagicMock

from django.core.cache import cache
from django.test import TestCase, override_settings

from .. import paypal_api
from ..models import Campaign, Fundraiser, Donation


@override_settings(
    PAYPAL_CLIENT_ID='test-client-id',
    PAYPAL_CLIENT_SECRET='test-secret',
    PAYPAL_API_BASE='https://api-m.sandbox.paypal.com',
    PAYPAL_WEBHOOK_ID='WH-TEST',
)
class TestPayPalAPI(TestCase):
    """Exercises paypal_api.py with mocked HTTP."""

    @classmethod
    def setUpTestData(cls):
        campaign = Campaign.objects.create(
            name='Test Campaign',
            goal=1000,
            campaign_message='Test',
            default_fundraiser_message='Default',
            default_fundraiser_amount=100,
        )
        fundraiser = Fundraiser.objects.create(
            campaign=campaign, name='Test Fundraiser', goal=500,
        )
        cls.donation = Donation.objects.create(
            fundraiser=fundraiser,
            name='Jane Donor',
            email='jane@example.com',
            amount=42.50,
            payment_method='paypal',
            payment_status='pending',
        )

    def setUp(self):
        cache.clear()

    def _mock_response(self, status_code=200, json_body=None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_body or {}
        response.text = json.dumps(json_body or {})
        return response

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    @patch('team_fundraising.paypal_api.requests.post')
    def test_get_access_token_fetches_and_caches(self, mock_post):
        # Use a real cache for this test; dev.py swaps in DummyCache during
        # test runs, which would defeat the caching assertion below.
        cache.clear()
        mock_post.return_value = self._mock_response(
            200, {'access_token': 'abc123', 'expires_in': 3600}
        )

        token = paypal_api.get_access_token()
        self.assertEqual(token, 'abc123')
        self.assertEqual(mock_post.call_count, 1)

        # Second call should hit the cache, not the API.
        token_again = paypal_api.get_access_token()
        self.assertEqual(token_again, 'abc123')
        self.assertEqual(mock_post.call_count, 1)

    @override_settings(PAYPAL_CLIENT_ID='', PAYPAL_CLIENT_SECRET='')
    def test_get_access_token_raises_without_credentials(self):
        with self.assertRaises(paypal_api.PayPalAPIError):
            paypal_api.get_access_token()

    @patch('team_fundraising.paypal_api.requests.post')
    def test_get_access_token_raises_on_http_error(self, mock_post):
        mock_post.return_value = self._mock_response(401, {'error': 'bad'})
        with self.assertRaises(paypal_api.PayPalAPIError):
            paypal_api.get_access_token()

    @patch('team_fundraising.paypal_api.requests.post')
    def test_create_order_sends_expected_payload(self, mock_post):
        # First call is token fetch, second is the order.
        mock_post.side_effect = [
            self._mock_response(200, {'access_token': 't', 'expires_in': 3600}),
            self._mock_response(201, {'id': 'ORDER-1', 'status': 'CREATED'}),
        ]

        result = paypal_api.create_order(self.donation)

        self.assertEqual(result['id'], 'ORDER-1')
        order_call = mock_post.call_args_list[1]
        self.assertIn('/v2/checkout/orders', order_call.args[0])
        sent = order_call.kwargs['json']
        self.assertEqual(sent['intent'], 'CAPTURE')
        self.assertEqual(sent['purchase_units'][0]['custom_id'], str(self.donation.id))
        self.assertEqual(sent['purchase_units'][0]['amount']['currency_code'], 'CAD')
        self.assertEqual(sent['purchase_units'][0]['amount']['value'], '42.50')

    @patch('team_fundraising.paypal_api.requests.post')
    def test_capture_order_hits_capture_endpoint(self, mock_post):
        mock_post.side_effect = [
            self._mock_response(200, {'access_token': 't', 'expires_in': 3600}),
            self._mock_response(201, {'id': 'ORDER-1', 'status': 'COMPLETED'}),
        ]

        result = paypal_api.capture_order('ORDER-1')

        self.assertEqual(result['status'], 'COMPLETED')
        capture_call = mock_post.call_args_list[1]
        self.assertIn('/v2/checkout/orders/ORDER-1/capture', capture_call.args[0])

    @patch('team_fundraising.paypal_api.requests.post')
    def test_verify_webhook_returns_true_on_success(self, mock_post):
        mock_post.side_effect = [
            self._mock_response(200, {'access_token': 't', 'expires_in': 3600}),
            self._mock_response(200, {'verification_status': 'SUCCESS'}),
        ]

        headers = {
            'paypal-auth-algo': 'SHA256withRSA',
            'paypal-cert-url': 'https://example/cert',
            'paypal-transmission-id': 'tid',
            'paypal-transmission-sig': 'sig',
            'paypal-transmission-time': '2026-01-01T00:00:00Z',
        }
        body = json.dumps({'event_type': 'PAYMENT.CAPTURE.COMPLETED'}).encode()

        self.assertTrue(paypal_api.verify_webhook(headers, body))

    @patch('team_fundraising.paypal_api.requests.post')
    def test_verify_webhook_returns_false_on_failure(self, mock_post):
        mock_post.side_effect = [
            self._mock_response(200, {'access_token': 't', 'expires_in': 3600}),
            self._mock_response(200, {'verification_status': 'FAILURE'}),
        ]
        body = json.dumps({'event_type': 'PAYMENT.CAPTURE.COMPLETED'}).encode()
        self.assertFalse(paypal_api.verify_webhook({}, body))

    def test_verify_webhook_rejects_when_webhook_id_unset(self):
        with override_settings(PAYPAL_WEBHOOK_ID=''):
            self.assertFalse(paypal_api.verify_webhook({}, b'{}'))

    @patch('team_fundraising.paypal_api.requests.post')
    def test_verify_webhook_rejects_unparseable_body(self, mock_post):
        self.assertFalse(paypal_api.verify_webhook({}, b'not-json'))
        mock_post.assert_not_called()

    @patch('team_fundraising.paypal_api.requests.post')
    def test_verify_webhook_returns_false_when_token_fetch_fails(
        self, mock_post,
    ):
        # Token endpoint returns 401 — verify_webhook must return False
        # rather than propagating PayPalAPIError (which would 500 the view).
        mock_post.return_value = self._mock_response(
            401, {'error': 'invalid_client'}
        )
        body = json.dumps({'event_type': 'PAYMENT.CAPTURE.COMPLETED'}).encode()
        self.assertFalse(paypal_api.verify_webhook({}, body))
