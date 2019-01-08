""" The forms for the team_fundraiser app
"""
from django import forms
from datetime import datetime
from django.forms import Form, Textarea, BooleanField, NumberInput
from .models import Donation, Fundraiser
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class DonationForm(forms.Form):
    """ Form for a new Donation, which can be tied to a specific fundraiser """

    name = forms.CharField()
    amount = forms.CharField()      
    other_amount = forms.CharField(required=False)                              
    email = forms.EmailField()
    anonymous = forms.BooleanField(required=False)
    date = datetime.now()
    
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
                amount = float(other_amount)
            except ValueError:
                raise forms.ValidationError("Amount is not a number")
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.is_staff = False
        user.is_admin = False

        if commit:
            user.save()

        return user
    

class FundraiserForm(forms.ModelForm):
    class Meta:
        model = Fundraiser
        fields = ('campaign', 'name', 'goal', 'message')