# Generated by Django 3.2.5 on 2023-05-02 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0053_alter_order_marketplace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='order number'),
        ),
    ]
