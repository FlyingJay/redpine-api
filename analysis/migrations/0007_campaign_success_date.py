# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-08 18:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0006_auto_20180208_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='success_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
