# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-19 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20171017_0129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='choice',
            name='poll',
        ),
        migrations.RemoveField(
            model_name='poll',
            name='answer_type',
        ),
        migrations.RemoveField(
            model_name='poll',
            name='choices_order',
        ),
        migrations.RemoveField(
            model_name='poll',
            name='question',
        ),
    ]
