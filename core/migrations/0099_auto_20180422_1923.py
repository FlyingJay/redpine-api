# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-22 19:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0098_auto_20180422_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='max_quantity',
            field=models.IntegerField(default=100, help_text='The number of this item available for sale.'),
        ),
    ]
