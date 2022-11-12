# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-10 19:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0009_band_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='created_by',
            field=models.ForeignKey(help_text='The user who created the campaign', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to=settings.AUTH_USER_MODEL),
        ),
    ]