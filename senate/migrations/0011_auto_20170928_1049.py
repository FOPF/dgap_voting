# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-28 07:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senate', '0010_auto_20170926_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='info',
            field=models.CharField(blank=True, default=None, max_length=2048, null=True, verbose_name='Информация'),
        ),
    ]