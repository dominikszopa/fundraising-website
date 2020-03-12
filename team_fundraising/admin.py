from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.views import View
from .models import Campaign, Fundraiser, Donation, Donor
from .register import signup_by_email


class CampaignAdmin(admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(Campaign)
admin.site.register(Fundraiser)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date', 'amount', 'payment_status',
        'email', 'fundraiser', 'country'
        )
    search_fields = ('name', 'email')
    list_filter = ('payment_status', 'country')


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    """
    Report that shows all the donations, grouped by email and name
    so that a single person donating to multiple fundraisers will show
    up once. Can be shown as HTML or exported as CSV
    """

    change_list_template = 'admin/donation_report.html'
    list_filter = ('fundraiser__campaign_id',)

    def changelist_view(self, request, extra_content=None):

        # call parent class
        response = super().changelist_view(
            request,
        )

        # if the user has chosen a campaign using the filter, pass it
        campaign_id = request.GET.get('fundraiser__campaign_id__id__exact', '')
        response.context_data['campaign_id'] = campaign_id

        # get the query string for the Donor proxy model
        try:
            donations = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # sort by number of donations - for some reason removing this
        # stops the grouping ??
        donations = donations.order_by('-amount')

        response.context_data['summary'] = list(
            donations
        )

        return response


class DonorCsv(View):
    """
    CSV export version of the Donor admin report, to be used from the admin
    section.
    """

    csv_template_name = 'admin/donation_report.csv'

    def get(self, request, campaign_id):

        # get donations for a single campaign
        donations = Donor.objects.filter(fundraiser__campaign_id=campaign_id)

        context = {
            'donations': donations,
            }

        # set up the csv content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="donations.csv"'

        t = loader.get_template(self.csv_template_name)
        context = {
                'donations': donations,
            }

        response.write(t.render(context))
        return response


class EmailSignup(View):
    """
    Show a form that allows signup of new fundraisers by email
    """

    template_name = 'admin/email_signup.html'

    def get(self, request):

        # get all campaigns
        campaigns = Campaign.objects.all()

        # display the form

        return render(request, self.template_name, {'campaigns': campaigns})

    def post(self, request):

        # get campaign
        campaign = get_object_or_404(Campaign, pk=request.POST['campaign'])
        email = request.POST['email']

        # TODO: loop through emails

        signup_by_email(request, campaign.id, email)

        #   store fundraisers in array

        return render(request, self.template_name)  # , fundraisers)
