# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-29 16:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_remove_bookingrequest_band'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingrequest',
            name='followed_up',
            field=models.BooleanField(default=False),
        ),
    ]
