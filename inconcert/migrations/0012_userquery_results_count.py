# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-04-03 03:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inconcert', '0011_auto_20200403_0241'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquery',
            name='results_count',
            field=models.IntegerField(default=None, null=True),
        ),
    ]