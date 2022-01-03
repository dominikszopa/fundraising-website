from team_fundraising.models import Campaign
from rest_framework import serializers


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['name', 'goal', 'get_total_raised']
