# Generated by Django 3.2.5 on 2023-05-15 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0058_auto_20230515_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='address',
            name='street_address',
        ),
    ]
