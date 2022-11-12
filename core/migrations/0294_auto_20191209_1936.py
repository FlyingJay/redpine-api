# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-09 19:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0293_navigationfeedback_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bandtobandreview',
            options={'verbose_name_plural': 'Reviews (Band > Band)'},
        ),
        migrations.AlterModelOptions(
            name='bandtovenuereview',
            options={'verbose_name_plural': 'Reviews (Band > Venue)'},
        ),
        migrations.AlterModelOptions(
            name='venuetobandreview',
            options={'verbose_name_plural': 'Reviews (Venue > Band)'},
        ),
        migrations.AddField(
            model_name='profile',
            name='is_ghost',
            field=models.BooleanField(default=False, help_text='Whether the account has been claimed or not.'),
        ),
    ]
