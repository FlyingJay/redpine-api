# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-14 02:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0285_auto_20191109_1748'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venue',
            name='default_fee_weekday',
        ),
        migrations.RemoveField(
            model_name='venue',
            name='default_fee_weekend',
        ),
        migrations.RemoveField(
            model_name='venue',
            name='default_headcount_weekday',
        ),
        migrations.RemoveField(
            model_name='venue',
            name='default_headcount_weekend',
        ),
    ]
