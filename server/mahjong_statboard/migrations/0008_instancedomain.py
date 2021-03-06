# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-18 15:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong_statboard', '0007_instance_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstanceDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='mahjong_statboard.Instance')),
            ],
        ),
    ]
