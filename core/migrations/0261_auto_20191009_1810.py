# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-09 18:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0260_auto_20191009_1504'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campaignband',
            options={'ordering': ['-start_time']},
        ),
    ]