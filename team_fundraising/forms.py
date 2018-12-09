from django.forms import ModelForm
from .models import Donation

class DonationForm(ModelForm):
    class Meta:
        model = Donation
        fields = ['name', 'amount', 'anonymous', 'email', 'message']
