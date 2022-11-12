# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-19 23:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_merge_20170819_1826'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bandartist',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='bandartist',
            name='band',
        ),
        migrations.RemoveField(
            model_name='band',
            name='members',
        ),
        migrations.AddField(
            model_name='artist',
            name='band',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='artists', to='core.Band'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='artist',
            name='is_creator',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(default='5cf5ac41bd58fa13', help_text='The unique ticket code', max_length=16),
        ),
        migrations.DeleteModel(
            name='BandArtist',
        ),
    ]
