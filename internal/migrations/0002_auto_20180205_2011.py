# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-05 20:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminnotification',
            name='on_create',
            field=models.BooleanField(default=False, help_text='Send a notification on create'),
        ),
        migrations.AddField(
            model_name='adminnotification',
            name='on_update',
            field=models.BooleanField(default=False, help_text='Send a notification on update'),
        ),
    ]
