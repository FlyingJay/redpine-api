# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-18 02:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0108_auto_20180517_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='bandtobandreview',
            name='responded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bandtovenuereview',
            name='responded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='venuetobandreview',
            name='responded',
            field=models.BooleanField(default=False),
        ),
    ]
