from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path('campaigns/', views.campaign_list),
    path('campaign/<int:pk>', views.campaign_detail),
]
