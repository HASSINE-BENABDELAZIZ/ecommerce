# Generated by Django 3.2.5 on 2023-05-16 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0011_alter_marketplace_secteur'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketplace',
            name='phone',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
