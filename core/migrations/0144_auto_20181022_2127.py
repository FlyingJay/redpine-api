# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-22 21:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0143_auto_20181020_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='description',
            field=models.TextField(max_length=2000),
        ),
    ]
