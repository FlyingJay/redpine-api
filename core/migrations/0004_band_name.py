# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 02:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170504_0200'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]