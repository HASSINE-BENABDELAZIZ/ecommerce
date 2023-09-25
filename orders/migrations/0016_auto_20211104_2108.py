# Generated by Django 3.2.5 on 2021-11-04 21:08

from django.db import migrations, models
import utils.s3


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_auto_20211104_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='label',
            field=models.FileField(blank=True, default=None, null=True, storage=utils.s3.PrivateMediaStorage(), upload_to='order_label'),
        ),
        migrations.AlterField(
            model_name='orderimports',
            name='file',
            field=models.FileField(default=None, storage=utils.s3.PrivateMediaStorage(), upload_to='csv_files'),
        ),
    ]
