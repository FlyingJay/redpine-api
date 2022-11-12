# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-25 21:16
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20170725_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='c48ff2c6cf3cee69', help_text='The unique ticket code', max_length=16),
        ),
        migrations.AlterField(
            model_name='venue',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326),
        ),
    ]
