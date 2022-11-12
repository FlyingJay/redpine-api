# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-10 19:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0010_auto_20190210_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='band',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='The user that created the band', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bands', to=settings.AUTH_USER_MODEL),
        ),
    ]