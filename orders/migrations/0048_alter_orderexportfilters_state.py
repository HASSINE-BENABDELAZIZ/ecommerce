# Generated by Django 3.2.5 on 2022-09-20 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0047_auto_20220919_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderexportfilters',
            name='state',
            field=models.CharField(blank=True, choices=[('Ben Arous', 'Ben Arous')], max_length=60, null=True, verbose_name='State'),
        ),
    ]
