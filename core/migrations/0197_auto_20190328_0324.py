# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-28 03:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('square', '0012_card'),
        ('core', '0196_auto_20190327_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledge',
            name='square_customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='square.Customer'),
        ),
        migrations.AlterField(
            model_name='pledge',
            name='customer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='stripper.Customer'),
        ),
    ]
