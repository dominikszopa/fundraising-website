from django.urls import path, include
from . import views
from .views import Paypal_donation, About, Donation_Report

app_name = 'team_fundraising'

urlpatterns = [
    path('', views.index_view, name='index'),
    path(
        'fundraiser/<int:fundraiser_id>/',
        views.fundraiser_view,
        name='fundraiser'
    ),
    path(
        'donation/<int:fundraiser_id>/', views.new_donation, name="donation"),
    path('paypal_donation/<int:fundraiser_id>/', Paypal_donation.as_view()),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path(
        'accounts/update_fundraiser/',
        views.update_fundraiser,
        name="update_fundraiser",
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name="signup"),
    path('about/', About.as_view(), name="about"),
    path(
        'donation_report/<int:campaign_id>/',
        Donation_Report.as_view(),
        name="donation_report"),
    path(
        'donation_report_csv/<int:campaign_id>/',
        Donation_Report.as_view(output_format="csv"),
        name="donation_report_csv"),
]
