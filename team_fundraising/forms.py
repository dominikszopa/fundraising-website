""" The forms for the team_fundraiser app
"""
from django import forms
from django.forms import Form, Textarea, BooleanField, NumberInput
from .models import Donation, Fundraiser

class DonationForm(forms.Form):
    """ Form for a new Donation, which can be tied to a specific fundraiser """

    name = forms.CharField()
    amount = forms.CharField()                                    
    email = forms.EmailField()
    anonymous = forms.BooleanField(required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows' : 3})) 

    """
    def clean(self):
        # Use the amount or "other amount" from the form
        cleaned_data = super(DonationForm, self).clean()

        amount = cleaned_data.get("amount")
        other_amount = cleaned_data.get("other_amount")

        if amount == -1:
            #TODO pull out just the number, in case they added a $
            try:
                amount = float(other_amount)
            except ValueError:
                amount = 0
    """

