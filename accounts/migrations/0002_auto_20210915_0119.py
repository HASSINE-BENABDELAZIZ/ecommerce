# Generated by Django 3.2.5 on 2021-09-15 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='test',
        ),
        migrations.RemoveField(
            model_name='user',
            name='test1',
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='media/avatar'),
        ),
    ]