# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-28 02:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0291_navigationfeedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='navigationfeedback',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='navigationfeedback',
            name='text',
            field=models.CharField(default='', max_length=5000),
        ),
    ]