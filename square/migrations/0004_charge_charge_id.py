# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-22 16:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('square', '0003_charge'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='charge_id',
            field=models.CharField(default='', help_text="The Square Charge object's ID", max_length=100),
            preserve_default=False,
        ),
    ]
