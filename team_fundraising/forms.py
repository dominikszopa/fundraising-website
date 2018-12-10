from django.forms import ModelForm, Textarea
from .models import Donation

class DonationForm(ModelForm):
    class Meta:
        model = Donation
        fields = ['name', 'amount', 'anonymous', 'email', 'message']

        widgets = {
            'message': Textarea(attrs={'cols':80, 'rows':3}),
        }

