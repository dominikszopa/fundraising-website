"""REST client for the PayPal Orders v2 API (Advanced Checkout).

Wraps the minimum surface we need: OAuth token fetch, order create/capture,
and webhook signature verification. We intentionally use ``requests`` plus
Django's cache instead of pulling in paypalserversdk — the surface is small
enough that the SDK would be more overhead than help.

All callable entry points raise :class:`PayPalAPIError` on failure so callers
can surface a single exception type to the user.
"""

import json
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

_TOKEN_CACHE_KEY = 'paypal:access_token'
# Subtract from PayPal's reported TTL so we never hand out a token that
# expires mid-request.
_TOKEN_SAFETY_MARGIN_SECONDS = 60
_HTTP_TIMEOUT_SECONDS = 30


class PayPalAPIError(Exception):
    """Raised when PayPal's REST API returns an error or unexpected response."""


def _api_base() -> str:
    """Return the PayPal REST API base URL for the configured environment."""
    return settings.PAYPAL_API_BASE.rstrip('/')


def _require_credentials() -> None:
    """Fail fast with a clear message if REST credentials are missing."""
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise PayPalAPIError(
            'PayPal REST credentials not configured. '
            'Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in your environment.'
        )


def get_access_token() -> str:
    """Return a cached OAuth2 access token, fetching a fresh one if needed."""
    cached = cache.get(_TOKEN_CACHE_KEY)
    if cached:
        return cached

    _require_credentials()

    response = requests.post(
        f'{_api_base()}/v1/oauth2/token',
        data={'grant_type': 'client_credentials'},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        headers={'Accept': 'application/json'},
        timeout=_HTTP_TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        logger.error(
            'PayPal token fetch failed: %s %s',
            response.status_code, response.text,
        )
        raise PayPalAPIError(
            f'Failed to obtain PayPal access token ({response.status_code})'
        )

    payload = response.json()
    token = payload['access_token']
    ttl = int(payload.get('expires_in', 32000)) - _TOKEN_SAFETY_MARGIN_SECONDS
    cache.set(_TOKEN_CACHE_KEY, token, timeout=max(ttl, 60))
    return token


def _auth_headers() -> dict:
    return {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json',
    }


def create_order(donation) -> dict:
    """Create a PayPal order for ``donation`` and return the order payload.

    ``custom_id`` is set to the Donation primary key so capture responses and
    webhook events can be correlated back to the row.
    """
    payload = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'reference_id': str(donation.id),
            'custom_id': str(donation.id),
            'invoice_id': f'TRIPLE_CROWN_{donation.id}',
            'description': 'Donation',
            'amount': {
                'currency_code': 'CAD',
                'value': f'{donation.amount:.2f}',
            },
        }],
    }
    response = requests.post(
        f'{_api_base()}/v2/checkout/orders',
        json=payload,
        headers=_auth_headers(),
        timeout=_HTTP_TIMEOUT_SECONDS,
    )
    if response.status_code not in (200, 201):
        logger.error(
            'PayPal create_order failed (donation=%s): %s %s',
            donation.id, response.status_code, response.text,
        )
        raise PayPalAPIError(
            f'Failed to create PayPal order ({response.status_code})'
        )
    return response.json()


def capture_order(order_id: str) -> dict:
    """Capture a previously-created PayPal order and return the payload."""
    response = requests.post(
        f'{_api_base()}/v2/checkout/orders/{order_id}/capture',
        json={},
        headers=_auth_headers(),
        timeout=_HTTP_TIMEOUT_SECONDS,
    )
    if response.status_code not in (200, 201):
        logger.error(
            'PayPal capture_order failed (order=%s): %s %s',
            order_id, response.status_code, response.text,
        )
        raise PayPalAPIError(
            f'Failed to capture PayPal order ({response.status_code})'
        )
    return response.json()


def verify_webhook(headers, body: bytes) -> bool:
    """Verify a webhook event's signature by asking PayPal to validate it.

    Arguments:
        headers: case-insensitive mapping (e.g. ``request.headers``).
        body: raw request body bytes as received from PayPal.

    Returns True only when PayPal responds with ``verification_status=SUCCESS``.
    """
    if not settings.PAYPAL_WEBHOOK_ID:
        logger.error('PAYPAL_WEBHOOK_ID is not configured; refusing to verify.')
        return False

    try:
        event = json.loads(body)
    except (TypeError, ValueError) as exc:
        logger.error('PayPal webhook body could not be parsed: %s', exc)
        return False

    payload = {
        'auth_algo': headers.get('paypal-auth-algo'),
        'cert_url': headers.get('paypal-cert-url'),
        'transmission_id': headers.get('paypal-transmission-id'),
        'transmission_sig': headers.get('paypal-transmission-sig'),
        'transmission_time': headers.get('paypal-transmission-time'),
        'webhook_id': settings.PAYPAL_WEBHOOK_ID,
        'webhook_event': event,
    }

    response = requests.post(
        f'{_api_base()}/v1/notifications/verify-webhook-signature',
        json=payload,
        headers=_auth_headers(),
        timeout=_HTTP_TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        logger.error(
            'PayPal verify_webhook failed: %s %s',
            response.status_code, response.text,
        )
        return False

    return response.json().get('verification_status') == 'SUCCESS'
