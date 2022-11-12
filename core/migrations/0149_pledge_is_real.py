# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-27 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0148_auto_20181027_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledge',
            name='is_real',
            field=models.BooleanField(default=False, help_text="Pledges are still created for direct-ticketed events, but they shouldn't be visible in the UI as such."),
        ),
    ]
