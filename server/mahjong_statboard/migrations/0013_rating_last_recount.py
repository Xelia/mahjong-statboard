# Generated by Django 2.0 on 2018-01-10 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahjong_statboard', '0012_rating_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='last_recount',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
