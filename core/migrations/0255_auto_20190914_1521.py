# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def make_many_genres(apps, schema_editor):
    Band = apps.get_model('core', 'Band')
    Venue = apps.get_model('core', 'Venue')

    for band in Band.objects.all():
    	if band.genre:
        	band.genres.add(band.genre)

    for venue in Venue.objects.all():
        if venue.primary_genre:
        	venue.genres.add(venue.primary_genre)
        if venue.secondary_genre:
        	venue.genres.add(venue.secondary_genre)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0254_venue_genres'),
    ]

    operations = [
        migrations.RunPython(make_many_genres),
    ]