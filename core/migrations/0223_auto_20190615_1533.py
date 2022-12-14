# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-06-15 15:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0222_remove_opening_open_mic'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='is_open_mic',
            field=models.BooleanField(default=False, help_text='Is the show a public open mic?'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_open',
            field=models.BooleanField(default=False, help_text='Is the show a public opportunity?'),
        ),
    ]
