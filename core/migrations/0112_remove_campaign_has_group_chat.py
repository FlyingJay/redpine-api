# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-03 14:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0111_auto_20180601_2354'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='has_group_chat',
        ),
    ]
