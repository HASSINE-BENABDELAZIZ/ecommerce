# Generated by Django 3.2.5 on 2021-10-07 18:50

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='breadcrumbmodel',
            name='name',
        ),
        migrations.AddField(
            model_name='breadcrumbmodel',
            name='utility',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), default=[['', '']], size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='breadcrumbmodel',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='url'),
        ),
    ]
