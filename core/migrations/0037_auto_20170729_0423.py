# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-29 04:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20170725_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='d1ab55a338cc3139', help_text='The unique ticket code', max_length=16),
        ),
    ]