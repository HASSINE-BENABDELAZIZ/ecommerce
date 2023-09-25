# Generated by Django 3.2.5 on 2022-09-15 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('accounts', '0021_user_marketplace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='marketplace',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketplace.marketplace'),
        ),
    ]
