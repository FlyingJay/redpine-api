# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-30 20:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20170630_2033'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pledge',
            old_name='cancelled',
            new_name='is_cancelled',
        ),
    ]