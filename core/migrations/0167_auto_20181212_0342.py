# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-12 03:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0166_hint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaignfeed',
            name='text',
            field=models.CharField(max_length=500),
        ),
    ]