from paypal.standard.models import ST_PP_COMPLETED


def process_paypal(sender, **kwargs):
    ipn_obj = sender
    print("received the signal...")
    print('ipn_obj.payment_status = ' + str(ipn_obj.payment_status))

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != "stephen@triplecrownforheart.com":
            # Not a valid payment
            print('not a valid payment.')
            return

        print('valid payment...')
        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        print('ipn_obj.custom = ' + str(ipn_obj.custom))

        # Undertake some action depending upon `ipn_obj`.
        if ipn_obj.custom == "premium_plan":
            price = 0
        else:
            price = 1

        if ipn_obj.mc_gross == price and ipn_obj.mc_currency == 'USD':
            print('USD')
    else:
        print('not completed')
