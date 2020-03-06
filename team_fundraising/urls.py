from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views
from .views import Paypal_donation, About, OneClickSignUp

app_name = 'team_fundraising'

urlpatterns = [
    path('', views.index_view_default, name='index_default'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('<campaign_id>/', views.index_view, name='index'),
    path(
        'fundraiser/<int:fundraiser_id>/',
        views.fundraiser_view,
        name='fundraiser'
    ),
    path('donation/<int:fundraiser_id>/', views.new_donation, name="donation"),
    path('paypal_donation/<int:fundraiser_id>/', Paypal_donation.as_view()),
    path(
        'accounts/update_fundraiser/',
        views.update_fundraiser,
        name="update_fundraiser",
    ),
    path(
        'accounts/update_fundraiser/<int:campaign_id>/',
        views.update_fundraiser,
        name="update_fundraiser",
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/<int:campaign_id>/', views.signup, name="signup"),
    path(
        'accounts/signup_logged_in/<int:campaign_id>/',
        login_required(OneClickSignUp.as_view()),
        name="signup_logged_in"
    ),
    path(
        'accounts/change_password/',
        views.change_password,
        name='change_password'
    ),
    path('about/<int:campaign_id>/', About.as_view(), name="about"),
]
