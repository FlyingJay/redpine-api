# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 01:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='min_ticket_price',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='min_ticket_price',
        ),
        migrations.RemoveField(
            model_name='timeslot',
            name='min_ticket_price',
        ),
    ]
