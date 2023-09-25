# Generated by Django 3.2.5 on 2023-06-14 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0064_auto_20230614_1137'),
        ('marketplace', '0012_alter_marketplace_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketplace',
            name='carrier',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.carrier'),
        ),
    ]
