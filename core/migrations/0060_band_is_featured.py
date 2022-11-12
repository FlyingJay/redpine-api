# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-26 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_auto_20170820_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='is_featured',
            field=models.BooleanField(default=False, help_text='Whether the band should be featured on our home page'),
        ),
    ]