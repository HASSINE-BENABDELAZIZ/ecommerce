# Generated by Django 3.2.5 on 2022-09-12 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0040_auto_20220908_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderexportfilters',
            name='state',
            field=models.CharField(blank=True, choices=[('BA', 'BA'), ('TN', 'TN'), ('so', 'so')], max_length=2, null=True, verbose_name='State'),
        ),
    ]
