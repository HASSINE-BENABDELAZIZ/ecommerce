# Generated by Django 3.2.5 on 2023-06-21 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0064_auto_20230614_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='barcode_filename',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]