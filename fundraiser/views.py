from django.shortcuts import render
from django.views import View
from team_fundraising.models import Campaign


class IndexView(View):
    # Show the list of active and inactive campaigns

    def get(self, request):

        active = Campaign.objects.filter(active=True)
        inactive = Campaign.objects.filter(active=False)
        template = 'index.html'

        context = {
            'active': active,
            'inactive': inactive,
        }

        return render(request, template, context)
