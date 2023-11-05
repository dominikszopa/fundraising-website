from paypal.standard.models import ST_PP_COMPLETED
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Donation
from .text import Donation_text


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

        # TODO: write these to the db or a file so we have some traceability
        # print(f"{ipn_obj.mc_gross}  {ipn_obj.mc_currency}")

        donation.payment_method = 'paypal'
        donation.payment_status = 'paid'
        donation.save()

        thank_you_email_text = (Donation_text.confirmation_email_opening
                                + '${:,.2f}'.format(donation.amount) + ' to '
                                + donation.fundraiser.name
                                + Donation_text.confirmation_email_closing_text)

        thank_you_email_html = (Donation_text.confirmation_email_opening
                                + '${:,.2f}'.format(donation.amount) + ' to '
                                + donation.fundraiser.name
                                + Donation_text.confirmation_email_closing_html)

        # send the thank you email
        send_mail(
            Donation_text.confirmation_email_subject,
            thank_you_email_text,
            'fundraising@triplecrownforheart.ca',
            [donation.email, ],
            html_message=thank_you_email_html
        )

        # send the notification email to the fundraiser
        send_mail(
            Donation_text.notification_email_subject,
            Donation_text.notification_email_opening
            + '${:,.2f}'.format(donation.amount) + ' from '
            + donation.name + " <" + donation.email + ">"
            + ' with the message:\n\n"' + donation.message + '"'
            + Donation_text.notification_email_closing,
            'fundraising@triplecrownforheart.ca',
            [donation.fundraiser.user.email, ]
        )

    else:
        print('not completed')
