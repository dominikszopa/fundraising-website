from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from .models import Campaign, Fundraiser, Donation
from .forms import DonationForm, UserForm, FundraiserForm, SignUpForm


def index_view(request):
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
    template = 'team_fundraising/fundraiser.html'

    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)
    donations = fundraiser.donation_set.order_by('-date')

    context = {
        'fundraiser': fundraiser,
        'donations': donations,
    }

    return render(request, template, context)


def new_donation(request, fundraiser_id):

    template = "team_fundraising/donation.html"

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
            donation.save()

            return redirect(
                'team_fundraising:fundraiser',
                fundraiser_id=fundraiser_id
            )

    else:
        form = DonationForm()
        fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

    context = {
        'form': form,
        'fundraiser': fundraiser,
    }

    return render(request, template, context)


def signup(request, campaign_id):
    # Create both a fundraiser and a user, tied together

    if request.method == "POST":

        user_form = SignUpForm(request.POST)
        fundraiser_form = FundraiserForm(request.POST)

        if user_form.is_valid() and fundraiser_form.is_valid():

            user = user_form.save()
            fundraiser = fundraiser_form.save()

            # tie this user to the fundraiser and save the model again
            fundraiser.user = user
            fundraiser.save()

            return redirect(
                'team_fundraising:fundraiser',
                fundraiser_id=fundraiser.id
            )
    else:
        user_form = SignUpForm()
        fundraiser_form = FundraiserForm()

    return render(request, 'registration/signup.html', {
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
            instance=request.user.fundraiser
        )

        if user_form.is_valid() and fundraiser_form.is_valid():

            user_form.save()
            fundraiser_form.save()
            # TODO: implement some type of success messaging and redirect
            # somewhere logical
            # messages.success(request, _("Your information was successfully
            # updated!"))
            return redirect('team_fundraising:update_fundraiser')

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
