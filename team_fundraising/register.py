from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Campaign, Fundraiser
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


def signup_by_email(request, campaign_id, name, email):
    """
    Sign up a user to a campaign by their email address. If the user already
    exists, add them as a fundraiser to the campaign. If the email address is
    in the campaign already, return that fundraiser.
    """

    campaign = get_object_or_404(Campaign, pk=campaign_id)

    # check if this email has been used
    user = User.objects.filter(
        email=email,
    )

    if not user:

        # create a user with this email address
        # TODO: set a random password and send it to them
        user = User.objects.create_user(
            username=email,
            email=email,
            password="random",
        )

        messages.success(request, 'Added user ' + email)

    # check for existing fundraiser
    fundraiser = Fundraiser.objects.filter(
        user__email=email,
        campaign_id=campaign_id
    )

    if not fundraiser:

        # pick the latest user
        user = User.objects.filter(email=email)[0]

        # add a fundraiser for this campaign
        fundraiser = Fundraiser(
            campaign=campaign,
            user=user,
            name=name,
            goal=200,
            message=campaign.default_fundraiser_message,
        )

        fundraiser.save()

        messages.success(
            request,
            'Added fundraiser id:' + str(fundraiser.id)
        )

        # send an email to the user
        send_new_fundraiser_email(request, fundraiser)

    else:

        fundraiser = fundraiser[0]

        messages.warning(
            request,
            'Fundraiser already exists id:' + str(fundraiser.id)
        )

    return fundraiser
