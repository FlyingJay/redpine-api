# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-20 00:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20170820_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='4ff82405cc7810d6', help_text='The unique ticket code', max_length=16),
        ),
    ]