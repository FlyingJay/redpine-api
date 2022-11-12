# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-15 20:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0230_auto_20190715_2032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsubscription',
            name='account_type',
            field=models.CharField(choices=[('ARTIST', 'ARTIST'), ('VENUE', 'VENUE')], help_text='artist or venue?', max_length=6),
        ),
        migrations.AlterField(
            model_name='accountsubscription',
            name='product_name',
            field=models.CharField(choices=[('MEMBER', 'MEMBER'), ('ULTIMATE', 'ULTIMATE')], help_text='What level was purchased?', max_length=8),
        ),
    ]
