# Generated by Django 2.1.2 on 2018-12-03 09:14

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team_fundraising', '0003_donation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 3, 1, 14, 58, 771273)),
        ),
        migrations.AlterField(
            model_name='donation',
            name='fundraiser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='team_fundraising.Fundraiser'),
        ),
    ]
