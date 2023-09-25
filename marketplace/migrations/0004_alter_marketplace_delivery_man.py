# Generated by Django 3.2.5 on 2023-04-24 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0050_alter_orderexportfilters_state'),
        ('marketplace', '0003_marketplace_delivery_man'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketplace',
            name='delivery_man',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.carrier'),
        ),
    ]
