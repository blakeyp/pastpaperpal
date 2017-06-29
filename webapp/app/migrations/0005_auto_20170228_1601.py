# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-28 16:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_usernotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='rubric',
            name='choice_choose',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='rubric',
            name='choice_text',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='rubric',
            name='time_mins',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='rubric',
            name='calcs_allowed',
            field=models.NullBooleanField(),
        ),
    ]
