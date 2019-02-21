from paypal.standard.models import ST_PP_COMPLETED
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Donation


def process_paypal(sender, **kwargs):
    ipn_obj = sender
    print("received the paypal signal...")
    print('ipn_obj.payment_status = ' + str(ipn_obj.payment_status))

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != settings.PAYPAL_ACCOUNT:
            # Not a valid payment
            print('not a valid payment.')
            return

        print('valid payment...')
        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        print('ipn_obj.custom = ' + str(ipn_obj.custom))

        donation = get_object_or_404(Donation, pk=ipn_obj.custom)

        donation.payment_method = 'paypal'
        donation.payment_status = 'paid'
        donation.save()

        # Undertake some action depending upon `ipn_obj`.
        if ipn_obj.custom == "premium_plan":
            price = 0
        else:
            price = 1

        if ipn_obj.mc_gross == price and ipn_obj.mc_currency == 'CAD':
            print(ipn_obj.mc_gross)
    else:
        print('not completed')
