# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-30 20:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20170630_2007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pledge',
            old_name='processed',
            new_name='is_processed',
        ),
    ]