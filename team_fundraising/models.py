""" Database models for the team_fundraising app

This module contains the models for the team_fundraising app, including a
parent Campaign, with individual Fundraisers, and Donations that can be raised
by the Fundraisers, or applied to the general Campaign.
"""
import os
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Max, Q, F, FloatField, Case, When
from django.db.models.functions import Coalesce
from django.conf import settings
from PIL import Image


class Campaign(models.Model):
    """
    The parent object that defines the campaign to which all Fundraisers
    and Donations belong.
    """

    name = models.CharField(max_length=50)
    goal = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    campaign_message = models.TextField()
    default_fundraiser_message = models.TextField()
    default_fundraiser_amount = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_total_raised(self):
        """
        Get the total raised from all Fundraisers
        """

        # get all paid donations in this campaign for all fundraisers
        donations = Donation.objects.filter(
            fundraiser__campaign__pk=self.id,
            payment_status='paid'
        )

        # sum the amounts
        donations = donations.aggregate(
            total=Sum('amount', output_field=FloatField())
        )
        total_raised = donations['total']

        # replace with zero if there are none
        if total_raised is None:
            total_raised = 0

        # get the "general" donations, ones not to a fundraiser
        general_donations = Donation.objects.filter(
            pk=self.id, fundraiser__isnull=True
        )

        # add general donations to total
        for donation in general_donations:
            total_raised += donation.amount

        return total_raised

    def get_fundraisers_with_totals(self):
        """
        Get all fundraisers in this campaign, with their raised totals
        already included. This is designed to be more efficient (less queries)
        then running a total_raised() call on each fundraiser.
        """

        # sum the amount of only "paid" donations
        paid_donations = Coalesce(Sum(
            'donation__amount',
            filter=Q(donation__payment_status__exact='paid'),
            output_field=FloatField()
            ), 0, output_field=FloatField())

        # filter only fundraisers in this campaign
        fundraisers = Fundraiser.objects.filter(campaign_id=self.id)

        # create the annotated query
        fundraisers = fundraisers.annotate(
            total_raised=paid_donations
            )

        # sort by total raised
        fundraisers = fundraisers.order_by('-total_raised')

        return fundraisers

    def get_recent_donations(self, num_donations):

        # get z recent "paid" donations by newest date
        recent_donations = Donation.objects.filter(
            fundraiser__campaign__id=self.id,
            payment_status__in=["paid", ""]
        ).order_by('-date')[:num_donations]

        return recent_donations

    @staticmethod
    def get_latest_active_campaign():

        campaign = Campaign.objects.filter(
            active=True
        ).first()

        return campaign


class Fundraiser(models.Model):
    """
    An individual fundraiser that has a goal and collects donations to their
    total and the campaigns.
    """

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, blank=True, null=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    goal = models.IntegerField(default=0, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True)
    photo_small = models.ImageField(upload_to='photos_small/', blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate and save the lower-resolution version of the photo
        if self.photo:
            with Image.open(self.photo) as img:
                img.thumbnail((800, 800))
                photo_dir, photo_filename = os.path.split(self.photo.name)
                new_photo_path = os.path.join('photos_small', photo_filename)
                img.save(os.path.join(settings.MEDIA_ROOT, new_photo_path))
                self.photo_small.name = new_photo_path

        super().save(*args, **kwargs)

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
        Get the total number of donators for this Fundraiser
        """
        total_donations = 0

        # get all paid donations for this fundraiser
        donations = Donation.objects.filter(
            fundraiser__pk=self.id,
            payment_status='paid'
        )

        # sum the donation amounts
        total_donations = donations.aggregate(total=Count('amount'))

        return total_donations['total']

    @staticmethod
    def get_latest_active_campaign(user_id):
        """
        Given a user id, find the most recent active fundraiser
        """

        # pick an active campaign with the highest number
        fundraiser = Fundraiser.objects.filter(
            user=user_id,
        ).order_by('-campaign__active', '-campaign__id').first()

        return fundraiser


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
    tax_name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    province = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=25, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.name


class DonorManager(models.Manager):
    """
    A model query manager that combines all donation by the donor
    based on email, name and campaign
    """

    def get_queryset(self):

        donations = super(DonorManager, self).get_queryset()

        # get all donations by campaign
        # and have been fully paid through paypal
        donations = donations.filter(
            payment_status='paid'
            )

        # group by email address and the tax_name provided
        # fill in name with the tax_name, but fall back to name if it's blank
        donations = donations.values(
                    'email',
                    'tax_name',
                    campaign_id=F('fundraiser__campaign_id'),
                    #  sum values, name is the tax_name if it exists
                    #  otherwise the name
                    ).annotate(
                        name=Case(
                            When(tax_name='', then=F('name')),
                            default=F('tax_name'),
                            output_field=models.CharField(),
                            ),
                        amount=Sum('amount'),
                        num_donations=Count('email'),
                        address=Max('address'),
                        city=Max('city'),
                        province=Max('province'),
                        postal_code=Max('postal_code'),
                        country=Max('country'),
                        date=Max('date'),
                    )

        return donations


class Donor(Donation):
    """
    A proxy model of the Donation model, used to summarize all the
    Donations by person, for reporting purposes.
    """

    objects = DonorManager()

    class Meta:
        proxy = True
        verbose_name = 'Donor'


class ProxyUser(User):
    """
    A proxy mode of the User model, to provide additional functions
    for the User
    """

    class Meta:
        proxy = True
        verbose_name = 'UserProxy'

    def get_latest_fundraiser(self):
        """
        Get a single, latest fundraiser for the user.
        For now, uses id order to identify the latest one.
        """

        fundraiser = Fundraiser.objects.filter(
            user_id=self.id
        ).order_by('id').first()

        return fundraiser
