# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-02 14:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venue_listings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='core_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='core_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='genre',
            name='core_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='province',
            name='core_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='venue',
            name='core_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]