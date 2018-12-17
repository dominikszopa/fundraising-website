""" The forms for the team_fundraiser app
"""
from django.forms import ModelForm, Textarea
from .models import Donation, Fundraiser

class DonationForm(ModelForm):
    """ Form for the Donation model. Used to create a new donation. """
    class Meta:
        model = Donation

        fields = ['name', 'amount', 'anonymous', 'email', 'message', 'fundraiser']

        widgets = {
            'message': Textarea(attrs={'cols':80, 'rows':3}),
        }

class FundraiserForm(ModelForm):
    """ Form for the Fundraiser model. Not currently used."""
    class Meta:
        model = Fundraiser

        fields = '__all__'
