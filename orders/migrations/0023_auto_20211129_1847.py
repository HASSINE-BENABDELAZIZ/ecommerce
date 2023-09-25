# Generated by Django 3.2.5 on 2021-11-29 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_auto_20211123_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderexportfiles',
            name='progress',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderexportfiles',
            name='task_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='orderexportfilters',
            name='state',
            field=models.CharField(blank=True, choices=[('AK', 'AK'), ('AL', 'AL'), ('AR', 'AR'), ('AZ', 'AZ'), ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DC', 'DC'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('IA', 'IA'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('MA', 'MA'), ('MD', 'MD'), ('ME', 'ME'), ('MI', 'MI'), ('MN', 'MN'), ('MO', 'MO'), ('MT', 'MT'), ('NC', 'NC'), ('ND', 'ND'), ('NE', 'NE'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NV', 'NV'), ('NY', 'NY'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('Tn', 'Tn'), ('VA', 'VA'), ('VT', 'VT'), ('WA', 'WA'), ('WI', 'WI'), ('WV', 'WV'), ('WY', 'WY'), ('te', 'te'), ('yy', 'yy')], max_length=2, null=True, verbose_name='State'),
        ),
    ]