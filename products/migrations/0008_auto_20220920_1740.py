# Generated by Django 3.2.5 on 2022-09-20 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20220920_1701'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name_plural': 'Sub Categories'},
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='products/', verbose_name='Image'),
        ),
    ]
