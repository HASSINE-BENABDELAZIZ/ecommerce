# Generated by Django 3.2.5 on 2023-04-24 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_alter_marketplace_delivery_man'),
        ('accounts', '0022_alter_user_marketplace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='marketplace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketplace.marketplace'),
        ),
    ]