# Generated by Django 3.2.5 on 2021-10-21 20:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_orderimports_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='Order_Number',
        ),
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.CharField(default=django.utils.timezone.now, max_length=255, unique=True, verbose_name='order number'),
            preserve_default=False,
        ),
    ]
