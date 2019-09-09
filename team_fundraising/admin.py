from django.contrib import admin
from .models import Campaign, Fundraiser, Donation


class CampaignAdmin(admin.ModelAdmin):
    pass


# Register your models here.

admin.site.register(Campaign)
admin.site.register(Fundraiser)
# admin.site.register(Donation)


@admin.register(Donation)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date', 'amount', 'payment_status',
        'email', 'fundraiser', 'country'
        )
    search_fields = ('name', 'email')
    list_filter = ('payment_status', 'country')
