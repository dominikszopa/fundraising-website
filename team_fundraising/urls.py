from django.urls import path

from . import views

app_name = 'team_fundraising'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('fundraiser/<int:fundraiser_id>/', views.fundraiser_view, name='fundraiser'),
    
]
