# Generated by Django 3.2.5 on 2022-09-14 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0041_alter_orderexportfilters_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrier',
            name='carrier',
            field=models.CharField(choices=[('gso', 'GSO'), ('fp', 'FP'), ('ups', 'UPS'), ('beezit', 'Beez it')], max_length=100, verbose_name='Carrier'),
        ),
    ]
