# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-01-14 22:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0294_auto_20191209_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='is_promotion',
            field=models.BooleanField(default=False, help_text='Whether or not RedPine is offering a promotion for bookings.'),
        ),
    ]
