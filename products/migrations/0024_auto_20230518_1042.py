# Generated by Django 3.2.5 on 2023-05-18 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_auto_20230516_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='currency',
            field=models.CharField(blank=True, default='TND', max_length=50, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.ImageField(blank=True, default=None, upload_to='products/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.BooleanField(blank=True, default=True, verbose_name='Active Status'),
        ),
        migrations.AlterField(
            model_name='product',
            name='upc',
            field=models.CharField(blank=True, max_length=255, verbose_name='UPC'),
        ),
        migrations.AlterField(
            model_name='product',
            name='year',
            field=models.IntegerField(blank=True, verbose_name='Year'),
        ),
    ]