# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-16 01:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0089_merge_20180312_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingrequest',
            name='is_crowdfunded',
            field=models.BooleanField(default=False),
        ),
    ]
