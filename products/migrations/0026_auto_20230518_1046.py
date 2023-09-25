# Generated by Django 3.2.5 on 2023-05-18 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0025_auto_20230518_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.CharField(max_length=255, verbose_name='Brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='currency',
            field=models.CharField(default='TND', max_length=50, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.ImageField(default=None, upload_to='products/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.BooleanField(default=True, verbose_name='Active Status'),
        ),
        migrations.AlterField(
            model_name='product',
            name='upc',
            field=models.CharField(max_length=255, verbose_name='UPC'),
        ),
        migrations.AlterField(
            model_name='product',
            name='year',
            field=models.IntegerField(verbose_name='Year'),
        ),
    ]