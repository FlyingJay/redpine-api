# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-27 16:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0214_venue_before_booking_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='before_booking_info',
            field=models.TextField(blank=True, default='', help_text='Extra info which an act should know before booking the venue. (Markdown)', max_length=5000),
        ),
    ]
