# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-22 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripper', '0007_auto_20170622_1947'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='customer_id',
            new_name='stripe_id',
        ),
        migrations.AddField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default='1970-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
