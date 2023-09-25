# Generated by Django 3.2.5 on 2022-09-08 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0037_auto_20220908_1109'),
        ('accounts', '0020_auto_20211025_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='marketplace',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.marketplace'),
        ),
    ]
