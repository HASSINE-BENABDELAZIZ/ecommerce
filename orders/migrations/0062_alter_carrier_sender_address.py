# Generated by Django 3.2.5 on 2023-05-18 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0061_auto_20230517_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrier',
            name='sender_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.address', verbose_name='Sender address'),
        ),
    ]
