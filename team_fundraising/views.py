from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django import forms
from .forms import DonationForm
from datetime import datetime

from .models import Campaign, Fundraiser, Donation

# Create your views here.

def index_view(request):
    template = 'team_fundraising/index.html'

    campaign = get_object_or_404(Campaign)

    fundraisers = sorted(campaign.fundraiser_set.all(), key=lambda x: x.total_raised(), reverse=True)
    general_donations = Donation.objects.filter(fundraiser__isnull=True)
    
    # get raised by fundraisers and add general donations
    total_raised = campaign.total_raised()
    for donation in general_donations :
        total_raised += donation.amount


    context = {
        'campaign' : campaign,
        'fundraisers' : fundraisers,
        'total_raised' : total_raised,
    }
    
    return render(request, template, context)

def fundraiser_view(request, fundraiser_id):
    template = 'team_fundraising/fundraiser.html'

    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)
    donations = fundraiser.donation_set.order_by('-date')

    context = {
        'fundraiser' : fundraiser,
        'donations' : donations,
    }

    return render(request, template, context)

def donate_view(request, fundraiser_id):

    template = 'team_fundraising/donate.html'

    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

    context = {
        'fundraiser' : fundraiser,
    }

    return render(request, template, context)

def donate_post(request, fundraiser_id):
    """Takes the submission of a donation form, and creates a new donation object to save to the model."""

    template = 'team_fundraising/donate_post.html'
    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

    donation = Donation()
    donation.fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)
    donation.name = request.POST['name']
    donation.message = request.POST['message']

    # Use the amount or "other amount" from the form
    if request.POST['amount'] == 'other' :
        # [TODO] pull out just the number, in case they added a $
        try:
            donation.amount = float(request.POST['other_amount'])
        except ValueError:
            return render(request, template, {
                'fundraiser' : fundraiser,
                'error_message' : "The donation amount is not recognized"
            })
    else :
        donation.amount = float(request.POST['amount'])

    # flag if they want to be anonymous
    if 'anonymous' in request.POST.keys() :
        if request.POST['anonymous'] == "Yes" : 
            donation.anonymous = True

    donation.date = datetime.now()
    donation.save()

    context = {
        'fundraiser' : fundraiser,
    }

    return render(request, template, context)


def new_donation(request, fundraiser_id):

    template = "team_fundraising/donation.html"

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.save()
            return redirect('/')
    else:
        form = DonationForm()
        return render(request, template, {'form': form})



class IndexView(generic.ListView):
    template_name = 'team_fundraising/index.html'
    model = Fundraiser
    context_object_name = 'fundraiser_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = "Triple Crown for Heart"
        return context

    def get_queryset(self):
        return Fundraiser.objects.order_by('-goal')

