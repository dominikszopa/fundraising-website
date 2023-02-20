""" The forms for the team_fundraiser app
"""
from django import forms
from django.utils import timezone
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
    tax_name = forms.CharField(label='Full Name', required=False)
    address = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=50, required=False)
    province = forms.CharField(max_length=50, required=False)
    country = forms.CharField(max_length=25, required=False)
    postal_code = forms.CharField(max_length=10, required=False)
    date = timezone.now()

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

        self.fields['username'].widget.attrs.pop("autofocus", None)

        self.fields['email'].required = True
        self.fields['username'].required = True

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

        self.fields['name'].required = True
        self.fields['goal'].required = True

        # disable all the fields if the campaign is no longer active
        if self.instance.pk is not None:

            if self.instance.campaign.active is False:

                for field in self.fields:
                    self.fields[field].disabled = True
