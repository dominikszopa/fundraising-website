"""fundraiser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from .views import IndexView
from team_fundraising.admin import DonorCsv


urlpatterns = [
    path('', IndexView.as_view()),
    path('team_fundraising/', include('team_fundraising.urls')),

    # Donation reports in the admin section
    path(
        'admin/donation_report_csv/<int:campaign_id>/',
        staff_member_required(DonorCsv.as_view()),
        name="donation_report_csv"
    ),
    path('admin/', admin.site.urls),

    # Had to add accounts here as well, as internal functions call it without
    # a namespace
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
