# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-25 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0273_auto_20191023_0316'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountsubscription',
            name='is_processing_failed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='accountsubscription',
            name='account_type',
            field=models.CharField(choices=[('ARTIST', 'ARTIST'), ('VENUE', 'VENUE'), ('ORGANIZER', 'ORGANIZER')], max_length=6),
        ),
    ]
