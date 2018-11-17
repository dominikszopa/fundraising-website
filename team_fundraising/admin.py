from django.contrib import admin
from .models import Campaign, Fundraiser, Donation

# Register your models here.

class CampaignAdmin(admin.ModelAdmin):
    pass

admin.site.register(Campaign)
admin.site.register(Fundraiser)
admin.site.register(Donation)