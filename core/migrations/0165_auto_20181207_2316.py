# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-07 23:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0164_bookingrequest_campaign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingrequest',
            name='campaign',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='first_request', to='core.Campaign'),
        ),
    ]
