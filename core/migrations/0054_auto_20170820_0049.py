# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-20 00:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20170820_0045'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artist',
            options={},
        ),
        migrations.AddField(
            model_name='artist',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='artist',
            name='confirmed',
            field=models.BooleanField(default=False, help_text='Whether the user has confirmed that they are in the band'),
        ),
    ]
