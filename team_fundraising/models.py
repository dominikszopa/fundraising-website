from django.db import models

# Create your models here.

class Campaign(models.Model):
    """
    The parent object that defines the campaign to which all Fundraisers 
    and Donations belong.
    """
    name = models.CharField(max_length=50)
    goal = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class Fundraiser(models.Model):
    """
    An individual fundraiser that has a goal and collects donations to their 
    total and the campaigns.
    """
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    goal = models.IntegerField(default=0)
    message = models.CharField(max_length=1000)
    def __str__(self):
        return self.name

class Donation(models.Model):
    """
    Individual donations that are made to a fundraiser. Note there is no
    "Donater" object, as each donation is treated as unique.
    :TODO: Make it possible for a donation not be tied to a fundraiser (direct to the Campaign)
    """
    fundraiser = models.ForeignKey(Fundraiser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    amount = models.FloatField(default=0)
    anonymous = models.BooleanField(default=False)
    email = models.EmailField()
    message = models.CharField(max_length=1000)
    payment_method = models.CharField(max_length=50)
    def __str__(self):
        return self.name
