# Generated by Django 4.2 on 2023-04-22 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_dadosajucard_cpf_alter_dadosrh_cpf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadosrh',
            name='pagar',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
