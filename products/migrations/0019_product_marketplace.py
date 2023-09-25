# Generated by Django 3.2.5 on 2023-05-01 22:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_alter_marketplace_delivery_man'),
        ('products', '0018_alter_product_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='marketplace',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketplace.marketplace'),
        ),
    ]
