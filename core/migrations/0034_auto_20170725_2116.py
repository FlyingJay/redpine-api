# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-25 21:16
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20170725_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0, 0, srid=4326), srid=4326),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='80b606ad76ccc535', help_text='The unique ticket code', max_length=16),
        ),
    ]