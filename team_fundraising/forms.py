""" The forms for the team_fundraiser app
"""
from django import forms
from django.forms import Form, Textarea, BooleanField, NumberInput
from .models import Donation, Fundraiser

class DonationForm(forms.Form):
    """ Form for a new Donation, which can be tied to a specific fundraiser """

    name = forms.CharField()
    amount = forms.CharField()      
    other_amount = forms.CharField(required=False)                              
    email = forms.EmailField()
    anonymous = forms.BooleanField(required=False)
    
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'required' : False,
             'rows' : 3}))

    
    def clean(self):
        # Use the amount or "other amount" from the form

        try:
            amount = self.cleaned_data['amount']
        except KeyError as e:
            amount = ""
        
        try:
            other_amount = self.cleaned_data['other_amount']
        except KeyError as e:
            other_amount = ""

        if amount == 'other' or amount == '':
            #TODO pull out just the number, in case they added a $
            try:
                self.cleaned_data['amount'] = float(other_amount)
            except ValueError:
                raise forms.ValidationError("Amount is not a number")
    

