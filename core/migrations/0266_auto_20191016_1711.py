# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-16 17:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0265_auto_20191014_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationband',
            name='is_accepted',
            field=models.NullBooleanField(default=None, help_text='Has the relation been confirmed by the act?'),
        ),
        migrations.AddField(
            model_name='organizationband',
            name='is_application',
            field=models.NullBooleanField(default=None, help_text='Has the relation been confirmed by the organization?'),
        ),
    ]
