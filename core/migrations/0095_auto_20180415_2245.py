# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-15 22:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0094_pledge_redpine_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pledge',
            name='redpine_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='The amount that the user has paid to RedPine', max_digits=6, verbose_name="RedPine's fee"),
        ),
    ]
