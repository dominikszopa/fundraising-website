from django.contrib import admin
from django.shortcuts import render
# from django.urls import path
from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum, Count, Max
from django.views import View
from .models import Campaign, Fundraiser, Donation


class CampaignAdmin(admin.ModelAdmin):
    pass


# Register your models here.

admin.site.register(Campaign)
admin.site.register(Fundraiser)


@admin.register(Donation)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date', 'amount', 'payment_status',
        'email', 'fundraiser', 'country'
        )
    search_fields = ('name', 'email')
    list_filter = ('payment_status', 'country')


"""
class DonationReport(admin.AdminSite):

    def get_urls(self):
        urls = super(DonationReport, self).get_urls()
        custom_urls = [
            path(
                'donation_report',
                self.admin_view(reports.donations),
                name="donation_report"
                ),
        ]
        return urls + custom_urls
"""


class Donation_Report(View):
    """
        Report that shows all the donations, grouped by email and name
        so that a single person donating to multiple fundraisers will show
        up once. Can be shown as HTML or exported as CSV
    """

    html_template_name = 'team_fundraising/donation_report.html'
    csv_template_name = 'team_fundraising/donation_report.csv'
    output_format = 'html'

    def get(self, request, campaign_id):

        # get all donations that are part of this campaign
        # and have been fully paid through paypal
        donations = Donation.objects.filter(
            fundraiser__campaign__pk=campaign_id,
            payment_status='paid')

        # group by email address
        donations = donations.values(
                    'email',
                    'name',
                    # sum some fields
                    ).annotate(
                        amount=Sum('amount'),
                        num_donations=Count('email'),
                        address=Max('address'),
                        city=Max('city'),
                        province=Max('province'),
                        postal_code=Max('postal_code'),
                        country=Max('country'),
                        date=Max('date'),
                    )

        # sort by number of donations
        donations = donations.order_by('-amount')

        context = {
            'donations': donations,
            'campaign_id': campaign_id
            }

        # if the user is requesting a .csv export
        if self.output_format == 'csv':
            print(self.output_format)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = \
                'attachment; filename="donations.csv"'

            t = loader.get_template(self.csv_template_name)
            context = {
                    'donations': donations,
                }

            response.write(t.render(context))
            return response

        else:

            # return the HTML version
            return render(
                request,
                self.html_template_name,
                context
            )
