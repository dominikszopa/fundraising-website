from django.core.mail import send_mail
from django.conf import settings
from .text import Fundraiser_text
from django.urls import reverse


def send_new_fundraiser_email(request, fundraiser):
    """
    Sends an email to a fundraiser who has successfully signed up
    """

    user = fundraiser.user

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


def signup_by_email(request, campaign_id, email):
    """
    Sign up a user to a campaign by their email address
    """

    # if a user exists for this email already

    #   pick the latest user
    #   if already tied to this campaign

    #       return a message with username

    #   else

    #       add this user to the campaign

    # else

    #    create a user
    #    create a fundraiser

    # send_new_fundraiser_email(request, fundraiser)
    # return fundraiser
