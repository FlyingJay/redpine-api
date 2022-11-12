# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-12 03:55
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0245_city_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, default=None, geography=True, null=True, srid=4326),
        ),
    ]