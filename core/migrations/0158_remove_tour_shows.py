# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-05 19:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0156_auto_20181105_1749'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='shows',
        ),
    ]