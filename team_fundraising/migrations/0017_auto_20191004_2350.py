# Generated by Django 2.2.4 on 2019-10-05 06:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('team_fundraising', '0016_auto_20190818_0111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donor',
            fields=[
            ],
            options={
                'verbose_name': 'Donor',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('team_fundraising.donation',),
        ),
        migrations.AlterField(
            model_name='donation',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
