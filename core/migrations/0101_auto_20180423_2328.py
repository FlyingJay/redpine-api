# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-23 23:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0100_auto_20180423_2159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='description',
        ),
        migrations.AddField(
            model_name='ticket',
            name='details',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.PurchaseItem'),
        ),
    ]
