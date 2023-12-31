# Generated by Django 3.2.5 on 2021-11-23 13:34

from django.db import migrations, models
import utils.s3


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_auto_20211121_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderexportfiles',
            name='file',
            field=models.FileField(blank=True, default=None, null=True, storage=utils.s3.PrivateMediaStorage(), upload_to='excel'),
        ),
        migrations.AlterField(
            model_name='orderexportfiles',
            name='status',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='status'),
        ),
    ]
