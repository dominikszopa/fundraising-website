import json
import logging

from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm

from . import paypal_api
from .models import Campaign, Fundraiser, Donation, ProxyUser
from .forms import DonationForm, UserForm, FundraiserForm, SignUpForm
from .text import Donation_text, Fundraiser_text
from .email_utils import send_email, send_donation_emails

logger = logging.getLogger(__name__)


@cache_page(60)
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


def _parse_json_body(request):
    """Return the decoded JSON body or None if it's not valid JSON."""
    try:
        return json.loads(request.body)
    except (TypeError, ValueError):
        return None


@require_POST
def create_donation_order(request, fundraiser_id):
    """Create a pending Donation and a PayPal order, return the order id.

    Called by the Advanced Checkout JS before the user confirms payment.
    Accepts form-encoded or JSON bodies so the frontend can post either.
    """
    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

    if request.content_type == 'application/json':
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        data = request.POST

    form = DonationForm(data)
    if not form.is_valid():
        return JsonResponse(
            {'error': 'Invalid form', 'fields': form.errors},
            status=400,
        )

    donation = Donation.objects.create(
        fundraiser=fundraiser,
        name=form.cleaned_data['name'],
        amount=float(form.cleaned_data['amount']),
        email=form.cleaned_data['email'],
        anonymous=form.cleaned_data['anonymous'],
        message=form.cleaned_data['message'],
        tax_name=form.cleaned_data['tax_name'],
        address=form.cleaned_data['address'],
        city=form.cleaned_data['city'],
        province=form.cleaned_data['province'],
        country=form.cleaned_data['country'],
        postal_code=form.cleaned_data['postal_code'],
        payment_method='paypal',
        payment_status='pending',
    )

    try:
        order = paypal_api.create_order(donation)
    except paypal_api.PayPalAPIError:
        logger.exception('PayPal create_order failed for donation %s', donation.id)
        return JsonResponse(
            {'error': 'Could not initiate payment. Please try again.'},
            status=502,
        )

    return JsonResponse({'orderID': order['id'], 'donationID': donation.id})


@require_POST
def capture_donation_order(request, donation_id):
    """Capture a PayPal order, verify its amount, and mark the donation paid.

    Uses an atomic UPDATE to guarantee emails are sent at most once, even
    if the webhook arrives before or after this call returns.
    """
    donation = get_object_or_404(Donation, pk=donation_id)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    order_id = data.get('orderID')
    if not order_id:
        return JsonResponse({'error': 'orderID required'}, status=400)

    try:
        capture = paypal_api.capture_order(order_id)
    except paypal_api.PayPalAPIError:
        logger.exception('PayPal capture_order failed for donation %s', donation.id)
        return JsonResponse(
            {'error': 'Could not complete payment.'},
            status=502,
        )

    if capture.get('status') != 'COMPLETED':
        logger.error(
            'PayPal capture status %s for donation %s',
            capture.get('status'), donation.id,
        )
        return JsonResponse({'error': 'Capture not completed'}, status=400)

    try:
        captured = (
            capture['purchase_units'][0]['payments']['captures'][0]['amount']
        )
        captured_amount = float(captured['value'])
        captured_currency = captured['currency_code']
    except (KeyError, IndexError, TypeError, ValueError):
        logger.exception(
            'Unexpected capture payload shape for donation %s', donation.id,
        )
        return JsonResponse({'error': 'Invalid capture response'}, status=502)

    # Guard against client-side amount tampering: PayPal's captured amount
    # is the authoritative figure, compared against what we stored.
    if (captured_currency != 'CAD'
            or abs(captured_amount - float(donation.amount)) > 0.01):
        logger.error(
            'Capture amount/currency mismatch for donation %s: '
            '%s %s vs expected %s CAD',
            donation.id, captured_amount, captured_currency, donation.amount,
        )
        return JsonResponse({'error': 'Amount mismatch'}, status=400)

    _mark_donation_paid(donation.id)

    return JsonResponse({'status': 'success', 'donationID': donation.id})


@csrf_exempt
@require_POST
def paypal_webhook(request):
    """Idempotent backstop for capture state — runs if the user closed the
    tab before ``capture_donation_order`` finished, or if PayPal retries.

    Verifies the signature with PayPal before trusting any field in the body.
    """
    if not paypal_api.verify_webhook(request.headers, request.body):
        logger.error('PayPal webhook signature verification failed')
        return HttpResponse(status=400)

    event = _parse_json_body(request)
    if event is None:
        return HttpResponse(status=400)

    if event.get('event_type') != 'PAYMENT.CAPTURE.COMPLETED':
        # Other event types are acknowledged but not acted on.
        return HttpResponse(status=200)

    custom_id = (event.get('resource') or {}).get('custom_id')
    if not custom_id:
        logger.error('PayPal webhook missing custom_id')
        return HttpResponse(status=400)

    try:
        donation_id = int(custom_id)
    except (TypeError, ValueError):
        logger.error('PayPal webhook bad custom_id: %s', custom_id)
        return HttpResponse(status=400)

    if not Donation.objects.filter(pk=donation_id).exists():
        logger.error('PayPal webhook for unknown donation: %s', donation_id)
        return HttpResponse(status=404)

    _mark_donation_paid(donation_id)
    return HttpResponse(status=200)


def _mark_donation_paid(donation_id):
    """Flip a donation from pending to paid and send emails once.

    Uses a conditional UPDATE so concurrent capture+webhook calls can't
    both trigger email sends.
    """
    rows = Donation.objects.filter(
        pk=donation_id, payment_status='pending',
    ).update(payment_status='paid')

    if rows:
        donation = Donation.objects.get(pk=donation_id)
        send_donation_emails(donation)


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
            send_email(
                Fundraiser_text.signup_email_subject,
                Fundraiser_text.signup_email_opening
                + request.build_absolute_uri(
                    reverse(
                        'team_fundraising:fundraiser', args=[fundraiser.id]
                    )
                )
                + "\n\nYour username is: " + user.username
                + Fundraiser_text.signup_email_closing,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
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

        campaign = get_object_or_404(Campaign, pk=campaign_id)

        if (request.user.is_authenticated):

            # pre-populate some values if signing up for another campaign
            user_form = SignUpForm(initial={
                'username': request.user.username,
                'email': request.user.email,
                })
        else:
            user_form = SignUpForm()

        fundraiser_form = FundraiserForm(
            initial={'goal': campaign.default_fundraiser_amount}
        )

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

        # Only carry the photo over if the original file still exists on
        # disk; otherwise Fundraiser.save() can't regenerate the thumbnail.
        prev_photo = previous_fundraiser.photo
        photo = (
            prev_photo
            if prev_photo and prev_photo.storage.exists(prev_photo.name)
            else None
        )

        # Create a new fundraiser using previous information and
        # defaults for the campaign
        new_fundraiser = Fundraiser(
            campaign=campaign,
            user=user,
            name=previous_fundraiser.name,
            team=previous_fundraiser.team,
            goal=campaign.default_fundraiser_amount,
            photo=photo,
            message=previous_fundraiser.message,
        )
        if photo is None and previous_fundraiser.photo_small:
            new_fundraiser.photo_small.name = previous_fundraiser.photo_small.name

        new_fundraiser.save()

        messages.info(
            request,
            'You have signed up for ' + campaign.name +
            '. You can change any of your information below.'
        )

        # send them an email that they have successfully signed up
        send_email(
            Fundraiser_text.signup_email_subject,
            Fundraiser_text.signup_email_opening
            + request.build_absolute_uri(
                reverse(
                    'team_fundraising:fundraiser', args=[new_fundraiser.id]
                )
            )
            + "\n\nYour username is: " + user.username
            + Fundraiser_text.signup_email_closing,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
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

            # if not, fall back to their most recent fundraiser
            fundraiser = Fundraiser.objects.filter(
                user=request.user.id,
            ).order_by('-campaign__id').first()

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
