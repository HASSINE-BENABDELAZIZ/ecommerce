# Generated by Django 3.2.5 on 2022-09-20 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20220920_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='products/', verbose_name='Image'),
        ),
    ]