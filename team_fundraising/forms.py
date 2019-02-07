""" The forms for the team_fundraiser app
"""
from django import forms
from datetime import datetime
from .models import Fundraiser
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
            attrs={'required': False, 'rows': 3}
        ),
        required=False
    )

    def clean(self):
        # if the user chooses "other amount", make that the amount

        cleaned_data = super().clean()

        try:
            amount = cleaned_data.get("amount")
        except KeyError:
            amount = ""

        try:
            other_amount = cleaned_data.get("other_amount")
        except KeyError:
            other_amount = ""

        if amount == 'other' or amount == '':
            # TODO pull out just the number, in case they added a $
            try:
                cleaned_data['amount'] = float(other_amount)
            except ValueError:
                raise forms.ValidationError("Amount is not a number")

        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)


class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

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
        fields = ('campaign', 'name', 'goal', 'photo', 'message')
        widgets = {
            'campaign': forms.HiddenInput(),
            'message': forms.Textarea(attrs={'rows': 3, 'cols': 20}),
        }

    def __init__(self, *args, **kwargs):
        super(FundraiserForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        self.fields['name'].widget.attrs['size'] = 50
        self.fields['goal'].widget.attrs['size'] = 10
