# Generated by Django 3.2.5 on 2023-05-01 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_alter_marketplace_delivery_man'),
        ('orders', '0052_auto_20230501_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='marketplace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketplace.marketplace'),
        ),
    ]
