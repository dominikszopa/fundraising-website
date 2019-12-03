from django.shortcuts import render
from django.views import View
from team_fundraising.models import Campaign


class IndexView(View):
    # Just an empty page, instead of an error

    def get(self, request):

        campaigns = Campaign.objects.all()
        template = 'index.html'

        context = {
            'campaigns': campaigns
        }

        return render(request, template, context)
