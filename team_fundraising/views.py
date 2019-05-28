from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm

from .models import Campaign, Fundraiser, Donation
from .forms import DonationForm, UserForm, FundraiserForm, SignUpForm


def index_view(request):
    # The home page, shows all fundraisers and total raised

    template = 'team_fundraising/index.html'

    campaign = get_object_or_404(Campaign)

    fundraisers = sorted(
        campaign.fundraiser_set.all(),
        key=lambda x: x.total_raised(),
        reverse=True
    )

    general_donations = Donation.objects.filter(fundraiser__isnull=True)

    # get raised by fundraisers and add general donations
    total_raised = campaign.total_raised()
    for donation in general_donations:
        total_raised += donation.amount

    context = {
        'campaign': campaign,
        'fundraisers': fundraisers,
        'total_raised': total_raised,
    }

    return render(request, template, context)


def fundraiser_view(request, fundraiser_id):
    # An individual's fundraising page, including total and donations

    template = 'team_fundraising/fundraiser.html'

    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

    if fundraiser.goal != 0:
        fundraiser.percent_raised = int(
            fundraiser.total_raised()) / fundraiser.goal * 100

    donations = fundraiser.donation_set.filter(
        payment_status__in=["paid", ""]).order_by('-date')

    context = {
        'fundraiser': fundraiser,
        'donations': donations,
    }

    return render(request, template, context)


def new_donation(request, fundraiser_id):
    # Show donation page, on submit show confirmation and button to PayPal

    if request.method == "POST":

        form = DonationForm(request.POST)
        fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

        if form.is_valid():

            # populate the model with form values
            donation = Donation()
            donation.fundraiser = fundraiser
            donation.name = form.cleaned_data['name']
            donation.amount = form.cleaned_data['amount']
            donation.email = form.cleaned_data['email']
            donation.anonymous = form.cleaned_data['anonymous']
            donation.message = form.cleaned_data['message']
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

            context = {"form": form, 'donation': donation}

            # leave a message that the user will see on their return
            # from PayPal
            messages.add_message(
                request,
                messages.SUCCESS,
                "Thank you for your donation. \
                You may need to refresh \
                this page to see the donation."
            )

            return render(request, template_name, context)

    else:

        form = DonationForm()
        fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

    template = "team_fundraising/donation.html"

    context = {
        'form': form,
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
        context = {"form": form}

        return render(request, self.template_name, context)


def signup(request):
    # Create both a fundraiser and a user, tied together through a foreign key

    if request.method == "POST":

        user_form = SignUpForm(request.POST)
        fundraiser_form = FundraiserForm(request.POST, request.FILES)

        if user_form.is_valid() and fundraiser_form.is_valid():

            user = user_form.save()
            fundraiser = fundraiser_form.save()

            # tie this user to the fundraiser and save the model again
            fundraiser.user = user
            fundraiser.save()

            # send them an email that they have successfully signed up
            send_mail(
                'Welcome to fundraising for the Triple Crown for Heart!',
                'Thanks for signing up to fundraise with us!\n'
                'Your fundraising page can be found at:\n'
                + request.get_host()
                + reverse(
                    'team_fundraising:fundraiser', args=[fundraiser.id]
                )
                + "\n\nYour username is: " + user.username
                + "\n\n Post it to social media!\n",
                'fundraising@triplecrownforheart.ca', [user.email, ]
            )

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
                "Thank you for signing up. This is your fundraiser page. "
                "Please share with your friends"
            )

            return redirect(
                'team_fundraising:fundraiser',
                fundraiser_id=fundraiser.id,
            )

    else:

        user_form = SignUpForm()
        fundraiser_form = FundraiserForm(initial={'goal': 200})

    # Currently, this works with only the first campaign
    campaign = get_object_or_404(Campaign)

    return render(request, 'registration/signup.html', {
        'campaign': campaign,
        'user_form': user_form,
        'fundraiser_form': fundraiser_form,
    })


@login_required
# @transaction_atomic
def update_fundraiser(request):
    """
    Update the fundraiser's information, along with the user values
    """
    if request.method == 'POST':

        user_form = UserForm(request.POST, instance=request.user)
        fundraiser_form = FundraiserForm(
            request.POST,
            request.FILES,
            instance=request.user.fundraiser
        )

        if user_form.is_valid() and fundraiser_form.is_valid():

            user_form.save()
            fundraiser_form.save()
            # TODO: implement some type of success messaging and redirect
            # somewhere logical
            # messages.success(request, _("Your information was successfully
            # updated!"))
            return redirect(
                'team_fundraising:fundraiser',
                fundraiser_id=request.user.fundraiser.id
            )

        # TODO: implement messages when something is wrong
        # else:
        # messages.error(request, _("Please correct the information below"))

    else:
        user_form = UserForm(instance=request.user)
        fundraiser_form = FundraiserForm(instance=request.user.fundraiser)

    return render(
        request, 'team_fundraising/update_fundraiser.html',
        {
            'user_form': user_form,
            'fundraiser_form': fundraiser_form,
        }
    )


class About(View):

    template_name = 'team_fundraising/about.html'

    def get(self, request):

        return render(request, self.template_name)
