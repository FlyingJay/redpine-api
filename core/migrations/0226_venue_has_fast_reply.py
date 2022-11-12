# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-06-24 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0225_auto_20190623_1735'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='has_fast_reply',
            field=models.BooleanField(default=False, help_text='Whether or not the venue replies to messages in a timely manner..'),
        ),
    ]
