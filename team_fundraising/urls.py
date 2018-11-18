from django.urls import path

from . import views

app_name = 'team_fundraising'

urlpatterns = [
    path('', views.index_view, name='index'),
    
]
