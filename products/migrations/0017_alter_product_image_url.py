# Generated by Django 3.2.5 on 2023-04-25 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_alter_product_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Image'),
        ),
    ]
