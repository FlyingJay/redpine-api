# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-22 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_auto_20171021_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_alpha_user',
            field=models.BooleanField(default=False, help_text='Whether the user has reset their password for beta'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_venue_approved',
            field=models.NullBooleanField(choices=[(None, 'null'), (True, 'true'), (False, 'false')], default=None, help_text='Whether the venue has confirmed the campaign'),
        ),
    ]
