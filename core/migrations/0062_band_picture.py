# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-26 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_merge_20170826_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]