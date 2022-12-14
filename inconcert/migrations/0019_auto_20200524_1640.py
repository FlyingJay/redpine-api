# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-05-24 16:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('square', '0014_charge_exchange_rate'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inconcert', '0018_subscription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='profile',
        ),
        migrations.AddField(
            model_name='subscription',
            name='is_cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='is_processed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='is_processing_failed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='square_customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='square.Customer'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='inconcert_subscription', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
