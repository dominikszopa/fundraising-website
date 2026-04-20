from paypal.standard.models import ST_PP_COMPLETED
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Donation
from .email_utils import send_donation_emails


def process_paypal(sender, **kwargs):
    """
    Process the IPN notification from PayPal once a payment is made

    Arguments:
    sender.custom is the donation id
    """
    ipn_obj = sender
    print("received the paypal signal...")
    print(f"ipn_obj.payment_status = {ipn_obj.payment_status}")

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != settings.PAYPAL_ACCOUNT:
            # Not a valid payment
            print('not a valid payment.')
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.
        print(f"ipn_obj.custom (donation) = {ipn_obj.custom}")

        donation = get_object_or_404(Donation, pk=ipn_obj.custom)

        donation.payment_method = 'paypal'
        donation.payment_status = 'paid'
        donation.save()

        send_donation_emails(donation)

    else:
        print('not completed')
