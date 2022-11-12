# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-06 17:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20170730_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='last_day',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The last day this timeslot may be booked'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='0970f967e5e9eacc', help_text='The unique ticket code', max_length=16),
        ),
    ]
