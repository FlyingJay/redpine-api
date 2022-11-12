# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-04 05:29
from __future__ import unicode_literals

from django.db import migrations

def make_venues(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Venue = apps.get_model('core', 'Venue')
    Campaign = apps.get_model('core', 'Campaign')

    for campaign in Campaign.objects.all():
    	if campaign.venue_name and not campaign.timeslot.venue:
    		venue = Venue.objects.create(title=campaign.venue_name,is_hidden=True)
    		
    		if campaign.timeslot:
    			campaign.timeslot.venue = venue

    		campaign.timeslot.save()
    		campaign.save()
    		venue.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0279_auto_20191104_0517'),
    ]

    operations = [
    	migrations.RunPython(make_venues),
    ]
