""" Database models for the team_fundraising app

This module contains the models for the team_fundraising app, including a
parent Campaign, with individual Fundraisers, and Donations that can be raised
by the Fundraisers, or applied to the general Campaign.
"""
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Campaign(models.Model):
    """
    The parent object that defines the campaign to which all Fundraisers
    and Donations belong.
    """

    name = models.CharField(max_length=50)
    goal = models.IntegerField(default=0)
    campaign_message = models.CharField(max_length=5000)
    default_fundraiser_message = models.CharField(max_length=5000)

    def __str__(self):
        return self.name

    def total_raised(self):
        """
        Get the total raised from all Fundraisers
        """

        # get all paid donations in this campaign
        donations = Donation.objects.filter(
            fundraiser__campaign__pk=self.id,
            payment_status='paid'
        )

        # sum the amounts
        donations = donations.aggregate(total=Sum('amount'))

        # replace with zero if there are none
        if donations["total"] is None:
            donations["total"] = 0

        return donations["total"]


class Fundraiser(models.Model):
    """
    An individual fundraiser that has a goal and collects donations to their
    total and the campaigns.
    """
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.OneToOneField(
        User, blank=True, null=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    goal = models.IntegerField(default=0, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True)
    message = models.CharField(max_length=5000, blank=True)

    def __str__(self):
        return self.name

    def total_raised(self):
        """
        Get the sum of Donations for this Fundraiser
        """

        # get all paid donations for this fundraiser
        donations = Donation.objects.filter(
            fundraiser__pk=self.id,
            payment_status='paid'
        )

        # sum the donation amounts
        donations = donations.aggregate(total=Sum('amount'))

        # replace with 0 if there were none
        if donations["total"] is None:
            donations["total"] = 0

        return donations["total"]

    def total_donations(self):
        """
        Get the total number of donators for this Fundraisers
        """
        total_donations = 0

        for donations in self.donation_set.all():
            total_donations += 1

        return total_donations


class Donation(models.Model):
    """
    Individual donations that are made to a fundraiser. Note there is no
    "Donater" object, as each donation is treated as unique.
    """
    fundraiser = models.ForeignKey(
        Fundraiser, blank=True, null=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    amount = models.FloatField(default=0)
    anonymous = models.BooleanField(default=False)
    email = models.EmailField()
    message = models.CharField(max_length=280, blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    province = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=25, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    date = models.DateTimeField(default=datetime.now)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.name
