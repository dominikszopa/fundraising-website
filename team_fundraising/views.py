from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from datetime import datetime

from .models import Campaign, Fundraiser, Donation

# Create your views here.

def index_view(request):
    template = 'team_fundraising/index.html'

    campaign = get_object_or_404(Campaign)

    fundraisers = sorted(campaign.fundraiser_set.all(), key=lambda x: x.total_raised(), reverse=True)

    context = {
        'campaign' : campaign,
        'fundraisers' : fundraisers,
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
    """
    Takes the submission of a donation form, and creates a new donation 
    object to save to the model
    """

    donation = Donation()

    donation.fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)
    donation.amount = float(request.POST['amount'])
    donation.name = request.POST['name']
    donation.message = request.POST['message']

    if 'anonymous' in request.POST.keys() :
        if request.POST['anonymous'] == "Yes" : 
            donation.anonymous = True;

    donation.date = datetime.now()
    donation.save()

    template = 'team_fundraising/donate_post.html'

    fundraiser = get_object_or_404(Fundraiser, pk=fundraiser_id)

    context = {
        'fundraiser' : fundraiser,
    }

    return render(request, template, context)


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

