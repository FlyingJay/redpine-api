# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-05 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0158_remove_tour_shows'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='shows',
            field=models.ManyToManyField(related_name='tours', through='core.CampaignTour', to='core.Campaign'),
        ),
    ]
