# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-22 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0118_auto_20180708_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='funding_type',
            field=models.IntegerField(choices=[(0, 'GOAL_AMOUNT'), (1, 'GOAL_COUNT'), (2, 'HYBRID')], default=0),
        ),
    ]
