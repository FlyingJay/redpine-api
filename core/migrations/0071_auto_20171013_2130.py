# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-13 21:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0070_auto_20171013_2024'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='artist',
            unique_together=set([]),
        ),
    ]
