# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-14 00:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0128_campaigndocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaigndocument',
            name='name',
            field=models.CharField(blank=True, default='Document', max_length=200),
        ),
    ]