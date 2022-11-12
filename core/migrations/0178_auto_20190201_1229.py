# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-01 12:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0177_merge_20190131_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='template',
            field=models.CharField(default='NEW_ACT_SHOW_INVITE', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='adminmail',
            name='sender',
            field=models.ForeignKey(help_text='A user associated with the mail. (you)', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='band',
            name='join_token',
            field=models.CharField(blank=True, default='f0341e1a4f7ba1c171afb10ba4c34d2c', max_length=32, null=True),
        ),
    ]