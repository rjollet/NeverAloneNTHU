# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-04 07:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='sexuality',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='interested_in',
            field=models.IntegerField(choices=[(1, 'Men'), (2, 'Women'), (3, 'Both')], default=1),
            preserve_default=False,
        ),
    ]