# Generated by Django 5.1.5 on 2025-02-02 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fact_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_type',
            field=models.CharField(choices=[('R', 'RECU'), ('P', 'PREFORMA FACTURE'), ('F', 'FACTURE')], max_length=1),
        ),
    ]
