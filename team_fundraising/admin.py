from django.contrib import admin
from django.db.models import Case, CharField, Count, F, Max, Sum, When
from django.http import HttpResponse
from django.template import loader
from django.views import View
from .models import Campaign, Fundraiser, Donation, Donor


class CampaignAdmin(admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(Campaign)
# admin.site.register(Fundraiser)


@admin.register(Fundraiser)
class FundraiserAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'user_email', 'campaign', 'goal', 'total_raised'
        )

    def user_email(self, obj):
        if obj.user:
            return obj.user.email

    search_fields = ('name', 'campaign__name')
    list_filter = ('campaign__name', 'user')


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date', 'amount', 'payment_status',
        'email', 'fundraiser', 'country'
        )
    search_fields = ('name', 'email')
    list_filter = ('payment_status', 'country')


class YearListFilter(admin.SimpleListFilter):
    """Filter donors by the calendar year of their donations."""

    title = 'year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = (Donation.objects
                 .filter(payment_status='paid')
                 .dates('date', 'year', order='DESC'))
        return [(str(d.year), str(d.year)) for d in years]

    def queryset(self, request, queryset):
        # Year filtering is handled in changelist_view to avoid HAVING-clause
        # issues with the already-annotated DonorManager queryset.
        return queryset


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    """
    Report that shows all the donations, grouped by email and name
    so that a single person donating to multiple fundraisers will show
    up once. Can be shown as HTML or exported as CSV
    """

    change_list_template = 'admin/donation_report.html'
    list_filter = ('fundraiser__campaign_id', YearListFilter)

    def changelist_view(self, request, extra_content=None):

        # call parent class
        response = super().changelist_view(request)

        # if the user has chosen a campaign using the filter, pass it
        campaign_id = request.GET.get('fundraiser__campaign_id__id__exact', '')
        response.context_data['campaign_id'] = campaign_id

        year = request.GET.get('year', '')
        response.context_data['year'] = year

        try:
            cl_queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        if year:
            # Re-aggregate from the base Donation model filtered by year so
            # each donor appears once with their combined total. This avoids
            # HAVING-clause issues with the already-annotated DonorManager.
            base = Donation.objects.filter(payment_status='paid', date__year=year)
            if campaign_id:
                base = base.filter(fundraiser__campaign_id=campaign_id)
            donations = (
                base
                .values('email', 'tax_name')
                .annotate(
                    name=Case(
                        When(tax_name='', then=F('name')),
                        default=F('tax_name'),
                        output_field=CharField(),
                    ),
                    amount=Sum('amount'),
                    num_donations=Count('email'),
                    address=Max('address'),
                    city=Max('city'),
                    province=Max('province'),
                    postal_code=Max('postal_code'),
                    country=Max('country'),
                    date=Max('date'),
                )
                .order_by('-amount')
            )
        else:
            donations = cl_queryset.order_by('-amount')

        response.context_data['summary'] = list(donations)

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

        # set up the csv content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="donations.csv"'

        t = loader.get_template(self.csv_template_name)
        response.write(t.render({'donations': donations}))
        return response


class DonorYearCsv(View):
    """
    CSV export of the Donor admin report filtered by calendar year, aggregated
    across all campaigns.
    """

    csv_template_name = 'admin/donation_report.csv'

    def get(self, request, year):

        donations = (
            Donation.objects
            .filter(payment_status='paid', date__year=year)
            .values('email', 'tax_name')
            .annotate(
                name=Case(
                    When(tax_name='', then=F('name')),
                    default=F('tax_name'),
                    output_field=CharField(),
                ),
                amount=Sum('amount'),
                address=Max('address'),
                city=Max('city'),
                province=Max('province'),
                postal_code=Max('postal_code'),
                country=Max('country'),
                date=Max('date'),
            )
            .order_by('-amount')
        )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            f'attachment; filename="donations_{year}.csv"'

        t = loader.get_template(self.csv_template_name)
        response.write(t.render({'donations': donations}))
        return response
