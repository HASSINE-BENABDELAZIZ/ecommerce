# Generated by Django 3.2.5 on 2021-10-13 19:30

from django.db import migrations, models
import utils.s3


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, storage=utils.s3.S3Boto3StoragePublic(), upload_to='avatar'),
        ),
    ]
