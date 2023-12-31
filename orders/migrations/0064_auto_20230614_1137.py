# Generated by Django 3.2.5 on 2023-06-14 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0063_alter_address_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='DroppexCarrier',
            fields=[
                ('carrier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='orders.carrier')),
                ('code_api', models.CharField(max_length=100, verbose_name='Code API')),
                ('key_api', models.CharField(max_length=100, verbose_name='Clé API')),
            ],
            bases=('orders.carrier',),
        ),
        migrations.CreateModel(
            name='PDFDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='t_service',
            field=models.CharField(blank=True, choices=[('Livraison', 'LIVRAISON'), ('Echange', 'ECHANGE')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='carrier',
            name='account_number',
            field=models.CharField(max_length=255, verbose_name='Numéro de compte'),
        ),
        migrations.AlterField(
            model_name='carrier',
            name='carrier',
            field=models.CharField(choices=[('fp', 'FP'), ('colissimo', 'Colissimo'), ('beezit', 'Beez it'), ('droppex', 'Droppex')], max_length=100, verbose_name='Transporteur'),
        ),
        migrations.AlterField(
            model_name='carrier',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='carrier',
            name='sender_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.address', verbose_name="Adresse de l'expéditeur"),
        ),
    ]
