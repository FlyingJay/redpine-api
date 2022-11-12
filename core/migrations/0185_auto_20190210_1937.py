# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-10 19:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0184_actpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pledge',
            name='bands',
            field=models.ManyToManyField(related_name='pledges', to='core.CampaignBand', verbose_name='Going to see'),
        ),
    ]