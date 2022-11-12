# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-04 04:35
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0277_auto_20191029_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='venue',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='venue',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(blank=True, default=None, null=True),
        ),
    ]