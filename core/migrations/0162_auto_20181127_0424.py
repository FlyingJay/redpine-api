# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-27 04:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0161_auto_20181105_2021'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tourcampaign',
            options={'ordering': ['campaign__timeslot__start_time']},
        ),
    ]