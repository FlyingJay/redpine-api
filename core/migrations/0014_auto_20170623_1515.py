# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-23 15:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_pledge_bands'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='only_tickets',
        ),
        migrations.AlterField(
            model_name='ticket',
            name='number',
            field=models.CharField(help_text='The unique ticket number', max_length=256),
        ),
    ]
