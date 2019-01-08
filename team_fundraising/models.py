""" Database models for the team_fundraising app

This module contains the models for the team_fundraising app, including a parent
Campaign, with individual Fundraisers, and Donations that can be raised by the
Fundraisers, or applied to the general Campaign.
"""
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Campaign(models.Model):
    """
    The parent object that defines the campaign to which all Fundraisers
    and Donations belong.
    """
    name = models.CharField(max_length=50)
    goal = models.IntegerField(default=0)
    def __str__(self):
        return self.name

    def total_raised(self):
        """
        Get the total raised from all Fundraisers
        """
        total_donations = 0

        for fundraiser in self.fundraiser_set.all():
            total_donations += fundraiser.total_raised()

        return total_donations

class Fundraiser(models.Model):
    """
    An individual fundraiser that has a goal and collects donations to their
    total and the campaigns.
    """
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    goal = models.IntegerField(default=0)
    message = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

    def total_raised(self):
        """
        Get the sum of Donations for this Fundraiser
        """
        total_donations = 0

        for donations in self.donation_set.all():
            total_donations += donations.amount

        return total_donations
"""
@receiver(post_save, sender=User)
def create_fundraiser(sender, instance, created, **kwargs):
    if created:
        Fundraiser.objects.create(user=instance)
"""
@receiver(post_save, sender=User)
def save_fundraiser(sender, instance, created, **kwargs):
    if created:
        Fundraiser.objects.create(user=instance)
    instance.fundraiser.save()
    

class Donation(models.Model):
    """
    Individual donations that are made to a fundraiser. Note there is no
    "Donater" object, as each donation is treated as unique.
    """
    fundraiser = models.ForeignKey(Fundraiser, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    amount = models.FloatField(default=0)
    anonymous = models.BooleanField(default=False)
    email = models.EmailField()
    message = models.CharField(max_length=280)
    date = models.DateTimeField(default=datetime.now)
    payment_method = models.CharField(max_length=50)
    def __str__(self):
        return self.name
