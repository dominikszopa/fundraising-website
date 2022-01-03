from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from rest_framework.parsers import JSONParser
from team_fundraising.models import Campaign
from .serializers import CampaignSerializer


@csrf_exempt
def campaign_list(request):
    """
    List all campaigns?
    """

    if request.method == 'GET':
        campaigns = Campaign.objects.all()
        serializer = CampaignSerializer(campaigns, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def campaign_detail(request, pk):
    """
    Get campaign details
    """
    try:
        campaign = Campaign.objects.get(pk=pk)
    except Campaign.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = CampaignSerializer(campaign)
        return JsonResponse(serializer.data)
