# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-25 18:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20170725_1845'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='city',
            options={'verbose_name_plural': 'Cities'},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'verbose_name_plural': 'countries'},
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='province',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='c5a876a76a82cbbf', help_text='The unique ticket code', max_length=16),
        ),
    ]