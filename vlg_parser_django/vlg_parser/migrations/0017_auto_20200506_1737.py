# Generated by Django 2.2.10 on 2020-05-06 17:37

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vlg_parser', '0016_auto_20200506_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='interesting_offers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=512, null=True), blank=True, null=True, size=None, verbose_name='Интересные предложения'),
        ),
    ]
