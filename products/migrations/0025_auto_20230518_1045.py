# Generated by Django 3.2.5 on 2023-05-18 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_auto_20230518_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.CharField(blank=True, max_length=255, verbose_name='Brand'),
        ),
    ]
