# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-20 00:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_auto_20170820_0042'),
    ]

    operations = [
        migrations.RenameField(
            model_name='band',
            old_name='deleted',
            new_name='archived',
        ),
    ]
