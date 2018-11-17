from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Campaign, Fundraiser, Donation

# Create your views here.
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
