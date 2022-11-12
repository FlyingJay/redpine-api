# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-05 20:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0086_auto_20180226_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='capacity',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
