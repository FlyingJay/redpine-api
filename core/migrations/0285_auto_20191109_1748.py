# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-09 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0284_auto_20191105_1930'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appcardtransaction',
            name='attendee_count',
        ),
        migrations.RemoveField(
            model_name='appcashtransaction',
            name='attendee_count',
        ),
        migrations.RemoveField(
            model_name='pledge',
            name='attendee_count',
        ),
        migrations.AddField(
            model_name='ticket',
            name='attended',
            field=models.BooleanField(default=False),
        ),
    ]
