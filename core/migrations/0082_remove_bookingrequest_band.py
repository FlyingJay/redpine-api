# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-29 16:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0081_bookingrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookingrequest',
            name='band',
        ),
    ]
