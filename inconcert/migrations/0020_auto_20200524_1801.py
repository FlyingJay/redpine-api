# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-05-24 18:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inconcert', '0019_auto_20200524_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inconcert_subscription', to=settings.AUTH_USER_MODEL),
        ),
    ]
