# Generated by Django 3.2.5 on 2023-05-11 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0054_alter_order_order_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderexportfilters',
            options={'permissions': (('export-order', 'export_order'),)},
        ),
    ]
