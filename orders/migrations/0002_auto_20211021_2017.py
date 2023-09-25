# Generated by Django 3.2.5 on 2021-10-21 20:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import orders.models
import utils.s3


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderImports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default=None, max_length=255, null=True)),
                ('file', models.FileField(storage=utils.s3.PrivateMediaStorage(), upload_to='csv_files')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('finished_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),

        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name='order',
            name='origin',
            field=models.CharField(blank=True, choices=[('manual', 'Manually added'), ('csv', 'Imported from csv file'), ('shipstation', 'Imported from Shipstation')], default='manual', max_length=255, null=True, verbose_name='origin'),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('AC', 'ACTION REQUIRED'), ('NO', 'NEW ORDER'), ('Co', 'CONFIRMED'), ('Pr', 'PRINTED'), ('Pa', 'PACKED'), ('PT', 'PRE TRANSIT'), ('IT', 'IN TRANSIT'), ('D', 'COMPLETED'), ('F', 'PROBLEMS'), ('awaiting_shipment', 'Awaiting for shipment')], default='NO', max_length=255, null=True, verbose_name='status'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='City',
            field=models.CharField(max_length=255, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='order',
            name='Customer_Name',
            field=models.CharField(max_length=255, null=True, verbose_name='Customer Name'),
        ),
        migrations.AlterField(
            model_name='order',
            name='Customer_email',
            field=models.EmailField(blank=True, max_length=255, null=True, verbose_name='Customer email'),
        ),
        migrations.AlterField(
            model_name='order',
            name='Phone',
            field=models.CharField(max_length=255, null=True, verbose_name='Phone'),
        ),
        migrations.AlterField(
            model_name='order',
            name='State',
            field=models.CharField(max_length=2, null=True, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='order',
            name='Street_1',
            field=models.CharField(max_length=255, null=True, verbose_name='Street 1'),
        ),
        migrations.AlterField(
            model_name='order',
            name='Street_2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Street 2'),
        ),
        migrations.AlterField(
            model_name='order',
            name='Zip_Code',
            field=models.CharField(max_length=5, null=True, validators=[orders.models.only_int], verbose_name='Zip_Code'),
        ),
        migrations.AlterField(
            model_name='orderitems',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='orderitems',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[orders.models.validate_number]),
        ),
        migrations.AlterField(
            model_name='orderitems',
            name='sku',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
