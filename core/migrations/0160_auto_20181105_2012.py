# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-05 20:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0159_tour_shows'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CampaignTour',
            new_name='TourCampaign',
        ),
    ]