# Generated by Django 2.2.10 on 2020-03-08 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_fundraising', '0021_auto_20200308_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='default_fundraiser_message',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='fundraiser',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
