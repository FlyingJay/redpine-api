# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-30 20:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20170630_2004'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='successful',
            new_name='is_successful',
        ),
        migrations.RenameField(
            model_name='campaign',
            old_name='venue_approved',
            new_name='is_venue_approved',
        ),
    ]
