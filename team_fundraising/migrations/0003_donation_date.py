# Generated by Django 2.1.2 on 2018-11-27 08:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_fundraising', '0002_auto_20181114_2213'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 27, 0, 17, 22, 324525)),
        ),
    ]
