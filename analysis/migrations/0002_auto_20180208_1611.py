# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-08 16:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='city',
        ),
        migrations.RemoveField(
            model_name='location',
            name='country',
        ),
        migrations.RemoveField(
            model_name='location',
            name='province',
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='analysis.Country'),
        ),
        migrations.AddField(
            model_name='city',
            name='province',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='analysis.Province'),
        ),
        migrations.AddField(
            model_name='venue',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='venues', to='analysis.City'),
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
