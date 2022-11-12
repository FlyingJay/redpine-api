# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-13 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20170813_1506'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeslot',
            name='last_day',
        ),
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='751297353e5785bb', help_text='The unique ticket code', max_length=16),
        ),
    ]
