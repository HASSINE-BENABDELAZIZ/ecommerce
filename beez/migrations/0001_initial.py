# Generated by Django 3.2.5 on 2022-09-15 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0043_alter_carrier_carrier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Beez',
            fields=[
                ('carrier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='orders.carrier')),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
            ],
            bases=('orders.carrier',),
        ),
    ]
