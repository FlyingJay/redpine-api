# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-16 13:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0133_auto_20180915_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaigndocument',
            name='document_type',
            field=models.CharField(blank=True, default='application/pdf', max_length=200),
        ),
    ]