# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-09 00:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='spotifyconnection',
            name='client_id',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]