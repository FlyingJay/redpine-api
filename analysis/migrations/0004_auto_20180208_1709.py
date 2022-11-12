# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-08 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0003_auto_20180208_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='core_id',
            field=models.IntegerField(help_text='/Core id value. Helps for generating the dataset.', null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='core_id',
            field=models.IntegerField(help_text='/Core id value. Helps for generating the dataset.', null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='core_id',
            field=models.IntegerField(help_text='/Core id value. Helps for generating the dataset.', null=True),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='core_id',
            field=models.IntegerField(help_text='/Core id value. Helps for generating the dataset.', null=True),
        ),
        migrations.AddField(
            model_name='venue',
            name='core_id',
            field=models.IntegerField(help_text='/Core id value. Helps for generating the dataset.', null=True),
        ),
    ]
