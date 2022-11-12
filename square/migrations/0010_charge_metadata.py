# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-09 01:37
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('square', '0009_customer_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default='{}', null=True),
        ),
    ]