# Generated by Django 3.2.5 on 2022-09-15 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_alter_user_marketplace'),
        ('orders', '0043_alter_carrier_carrier'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MarketPlace',
        ),
    ]
