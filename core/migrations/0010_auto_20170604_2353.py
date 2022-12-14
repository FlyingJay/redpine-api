# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-04 23:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0009_auto_20170516_2347'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='artist',
            field=models.BooleanField(default=False, help_text='Does the user want to see artist sections of the app?'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='venue',
            field=models.BooleanField(default=False, help_text='Does the user want to see venue sections of the app?'),
        ),
    ]
