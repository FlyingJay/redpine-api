# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-02 15:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0212_auto_20190501_1449'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'verbose_name_plural': 'Countries'},
        ),
        migrations.AlterModelOptions(
            name='province',
            options={'verbose_name_plural': 'Provinces'},
        ),
    ]
