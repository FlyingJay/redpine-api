# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-04 16:35
from __future__ import unicode_literals

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0153_auto_20181101_0037'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='total_count',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='total_raised',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=6, null=True, validators=[core.validators.non_negative]),
        ),
    ]
