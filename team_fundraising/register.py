from django.core.mail import send_mail
from django.conf import settings
from .text import Fundraiser_text
from django.urls import reverse


def send_new_fundraiser_email(request, user, fundraiser):
    """
    Sends an email to a fundraiser who has successfully signed up
    """

    send_mail(
        Fundraiser_text.signup_email_subject,
        Fundraiser_text.signup_email_opening
        + request.build_absolute_uri(
            reverse(
                'team_fundraising:fundraiser', args=[fundraiser.id]
            )
        )
        + "\n\nYour username is: " + user.username
        + Fundraiser_text.signup_email_closing,
        'fundraising@triplecrownforheart.ca',
        [user.email, ],
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD
    )
