# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-23 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_ticket_pledge'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledge',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
