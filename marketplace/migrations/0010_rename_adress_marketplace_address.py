# Generated by Django 3.2.5 on 2023-05-16 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0009_rename_tel_marketplace_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='marketplace',
            old_name='adress',
            new_name='address',
        ),
    ]
