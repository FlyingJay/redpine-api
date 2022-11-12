# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-14 13:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0250_remove_genre_depth'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenreParent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='genre',
            name='parent',
        ),
        migrations.AddField(
            model_name='genreparent',
            name='genre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_parents', to='core.Genre'),
        ),
        migrations.AddField(
            model_name='genreparent',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_children', to='core.Genre'),
        ),
        migrations.AddField(
            model_name='genre',
            name='parents',
            field=models.ManyToManyField(help_text='The parent genres, if applicable.', related_name='children', through='core.GenreParent', to='core.Genre'),
        ),
    ]