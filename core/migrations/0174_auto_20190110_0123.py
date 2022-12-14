# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-10 01:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0173_campaign_is_redpine_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='is_redpine_approved',
            field=models.NullBooleanField(choices=[(None, 'null'), (True, 'true'), (False, 'false')], default=True, help_text='Whether RedPine has approved the campaign to be sent to the venue'),
        ),
    ]
