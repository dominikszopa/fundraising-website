from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm

from .models import Campaign, Fundraiser, Donation, ProxyUser
from .forms import DonationForm, UserForm, FundraiserForm, SignUpForm
from .text import Donation_text, Fundraiser_text


def index_view(request, campaign_id):
    # The home page, shows all fundraisers and total raised

    template = 'team_fundraising/index.html'

    campaign = get_object_or_404(Campaign, pk=campaign_id)

    fundraisers = campaign.get_fundraisers_with_totals()

    # get 5 recent "paid" donations by newest date
    recent_donations = campaign.get_recent_donations(5)

    # get raised by fundraisers and add general donations
    total_raised = campaign.get_total_raised()

    context = {
        'campaign': campaign,
        'fundraisers': fundraisers,
        'total_raised': total_raised,
        'recent_donations': recent_donations,
    }

    return render(request, template, context)


def index_view_default(request):

    campaign = Campaign.get_latest_active_campaign()

    return index_view(request, campaign.id)


def fundraiser_view(request, fundraiser_id):
    # An individual's fundraising page, including total and donations

    template = 'team_fundraising/fundraiser.html'

    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)
    campaign = get_object_or_404(Campaign, pk=fundraiser.campaign_id)

    fundraiser.total_raised = fundraiser.total_raised()

    if fundraiser.goal != 0:
        fundraiser.percent_raised = int(
            fundraiser.total_raised) / fundraiser.goal * 100

    donations = fundraiser.donation_set.filter(
        payment_status__in=["paid", ""]).order_by('-date')

    context = {
        'campaign': campaign,
        'fundraiser': fundraiser,
        'donations': donations,
    }

    return render(request, template, context)


def new_donation(request, fundraiser_id):
    # Show donation page, on submit show confirmation and button to PayPal

    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)
    campaign = Campaign.objects.filter(fundraiser=fundraiser_id).first()

    if request.method == "POST":

        form = DonationForm(request.POST)

        if form.is_valid():

            # populate the model with form values
            donation = Donation()
            donation.fundraiser = fundraiser
            donation.name = form.cleaned_data['name']
            donation.amount = form.cleaned_data['amount']
            donation.email = form.cleaned_data['email']
            donation.anonymous = form.cleaned_data['anonymous']
            donation.message = form.cleaned_data['message']
            donation.tax_name = form.cleaned_data['tax_name']
            donation.address = form.cleaned_data['address']
            donation.city = form.cleaned_data['city']
            donation.province = form.cleaned_data['province']
            donation.country = form.cleaned_data['country']
            donation.postal_code = form.cleaned_data['postal_code']
            donation.payment_method = 'paypal'
            donation.payment_status = 'pending'
            donation.save()

            paypal_dict = {
                "bn": "TripleCrown_Donate_WPS_CA",
                "business": settings.PAYPAL_ACCOUNT,
                "amount": donation.amount,
                "currency_code": "CAD",
                "item_name": "Donation",
                "invoice": "TRIPLE_CROWN_"+str(donation.id),
                "notify_url": request.build_absolute_uri(
                    reverse('team_fundraising:paypal-ipn')
                    ),
                "return": request.build_absolute_uri(
                    reverse(
                        'team_fundraising:fundraiser', args=[fundraiser_id])
                    ),
                "cancel_return": request.build_absolute_uri(
                    reverse(
                        'team_fundraising:fundraiser', args=[fundraiser_id])
                    ),
                "custom": donation.id,
            }

            template_name = 'team_fundraising/paypal_donation.html'

            # create the instance
            form = PayPalPaymentsForm(
                initial=paypal_dict, button_type="donate")

            context = {
                "form": form,
                'donation': donation,
                'campaign': campaign,
                }

            # leave a message that the user will see on their return
            # from PayPal
            messages.add_message(
                request,
                messages.SUCCESS,
                Donation_text.thank_you
            )

            return render(request, template_name, context)

    else:

        form = DonationForm()

    template = "team_fundraising/donation.html"

    context = {
        'form': form,
        'campaign': campaign,
        'fundraiser': fundraiser,
    }

    return render(request, template, context)


class Paypal_donation(View):
    # initial test of the paypal donation - no longer used

    template_name = 'team_fundraising/paypal_donation.html'

    def get(self, request, fundraiser_id):

        paypal_dict = {
            "bn": "TripleCrown_Donate_WPS_CA",
            "business": settings.PAYPAL_ACCOUNT,
            "amount": "50.00",
            "currency_code": "CAD",
            "item_name": "Donation",
            "invoice": "unique-invoice-id",
            "notify_url": request.build_absolute_uri(
                reverse('team_fundraising:paypal-ipn')
                ),
            "return": request.build_absolute_uri(
                reverse('team_fundraising:fundraiser', args=[fundraiser_id])
                ),
            "cancel_return": request.build_absolute_uri(
                reverse('team_fundraising:fundraiser', args=[fundraiser_id])
                ),
            "custom": fundraiser_id,
        }

        # create the instance
        form = PayPalPaymentsForm(initial=paypal_dict, button_type="donate")
        context = {
            "form": form
            }

        return render(request, self.template_name, context)


def signup(request, campaign_id):
    # Create both a fundraiser and a user, tied together through a foreign key

    if request.method == "POST":

        fundraiser_form = FundraiserForm(request.POST, request.FILES)
        user_form = SignUpForm(request.POST)

        # if you are adding a fundraiser to an existing user
        if User.objects.filter(username=request.POST['username']).exists():

            if fundraiser_form.is_valid():

                if request.user.is_authenticated:

                    user = request.user

                else:

                    # check if the password is correct
                    user = authenticate(
                        request,
                        username=request.POST['username'],
                        password=request.POST['password1']
                    )

                if user is not None:

                    # check to see if there is already a fundraiser
                    # in this campaign
                    if Fundraiser.objects.filter(
                        user=user.id,
                        campaign=campaign_id,
                    ).exists():

                        login(request, user)

                        # send them to the update fundraiser page
                        return redirect('team_fundraising:update_fundraiser')

                else:

                    messages.error(
                        request,
                        Fundraiser_text.signup_wrong_password_existing_user,
                        extra_tags='safe',
                        )

                    campaign = get_object_or_404(Campaign, pk=campaign_id)

                    return render(request, 'registration/signup.html', {
                        'campaign': campaign,
                        'user_form': user_form,
                        'fundraiser_form': fundraiser_form,
                    })

        else:  # new user

            if user_form.is_valid() and fundraiser_form.is_valid():

                user = user_form.save()

        if fundraiser_form.is_valid():

            fundraiser = fundraiser_form.save()

            # tie this user to the fundraiser and save the model again
            fundraiser.user = user
            fundraiser.save()

            # send them an email that they have successfully signed up
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
        else:  # not a valid fundraiser form

            messages.error(
                request,
                "Something went wrong. Please try again.",
                extra_tags='safe',
                )

            campaign = get_object_or_404(Campaign, pk=campaign_id)

            return render(request, 'registration/signup.html', {
                'campaign': campaign,
                'user_form': user_form,
                'fundraiser_form': fundraiser_form,
            })

        if not request.user.is_authenticated:
            # log in the user so they don't have to do it now
            login_user = authenticate(
                request,
                username=request.POST['username'],
                password=request.POST['password1']
            )

            if login_user is not None:
                login(request, user)

        messages.info(
            request,
            Fundraiser_text.signup_return_message
        )

        return redirect(
            'team_fundraising:fundraiser',
            fundraiser_id=fundraiser.id,
        )

    else:  # GET

        if (request.user.is_authenticated):

            # pre-populate some values if signing up for another campaign
            user_form = SignUpForm(initial={
                'username': request.user.username,
                'email': request.user.email,
                })
        else:
            user_form = SignUpForm()

        fundraiser_form = FundraiserForm(initial={'goal': 200})

    campaign = get_object_or_404(Campaign, pk=campaign_id)

    return render(request, 'registration/signup.html', {
        'campaign': campaign,
        'user_form': user_form,
        'fundraiser_form': fundraiser_form,
    })


class OneClickSignUp(View):
    """
    Create a new fundraiser in a new campaign for an existing user.
    Copies over information from the previous user.
    """

    def get(self, request, campaign_id):

        user = get_object_or_404(ProxyUser, pk=request.user.id)
        campaign = get_object_or_404(Campaign, pk=campaign_id)

        previous_fundraiser = user.get_latest_fundraiser()

        # Create a new fundraiser using previous information and
        # defaults for the campaign
        new_fundraiser = Fundraiser(
            campaign=campaign,
            user=user,
            name=previous_fundraiser.name,
            goal=200,
            photo=previous_fundraiser.photo,
            message=previous_fundraiser.message,
        )

        new_fundraiser.save()

        messages.info(
            request,
            'You have signed up for ' + campaign.name
        )

        # send them to the update fundraiser page
        return redirect('team_fundraising:update_fundraiser', campaign_id)


@login_required
# @transaction_atomic
def update_fundraiser(request, campaign_id=None):
    """
    Update the fundraiser's information, along with the user values
    """

    # get the current active campaign, and the fundraiser entry for this user
    # if it exists
    active_campaign = Campaign.get_latest_active_campaign
    latest_fundraiser = Fundraiser.get_latest_active_campaign(request.user.id)

    # if no campaign id is included, get the latest one by default
    if (campaign_id is None):

        fundraiser = latest_fundraiser

    else:

        try:
            # try to get the fundraiser for this campaign
            fundraiser = Fundraiser.objects.get(
                user=request.user.id,
                campaign_id=campaign_id,
            )

        except ObjectDoesNotExist:

            # if not, get a fundraiser for any campaign
            fundraiser = Fundraiser.objects.filter(
                user=request.user.id,
            ).first()

    if request.method == 'POST':

        user_form = UserForm(request.POST, instance=request.user)
        fundraiser_form = FundraiserForm(
            request.POST,
            request.FILES,
            instance=fundraiser
        )

        if user_form.is_valid() and fundraiser_form.is_valid():

            user_form.save()
            fundraiser_form.save()

            messages.success(request, 'Your information was updated')

            return redirect(
                'team_fundraising:fundraiser',
                fundraiser_id=fundraiser_form.instance.pk,
            )

    else:

        user_form = UserForm(instance=request.user)

        fundraiser_form = FundraiserForm(
            instance=fundraiser
            )

    return render(
        request, 'team_fundraising/update_fundraiser.html',
        {
            'campaign': fundraiser.campaign,
            'user_form': user_form,
            'fundraiser_form': fundraiser_form,
            'active_campaign': active_campaign,
            'latest_fundraiser': latest_fundraiser,
        }
    )


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated')
            return redirect('team_fundraising:update_fundraiser')
        else:
            messages.error(
                request,
                'There is an error on the page. Please check and try again.'
                )
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request,
        'accounts/change_password.html',
        {'form': form}
        )


class About(View):

    template_name = 'team_fundraising/about.html'

    def get(self, request, campaign_id):

        campaign = get_object_or_404(Campaign, pk=campaign_id)

        return render(request, self.template_name, {'campaign': campaign})
