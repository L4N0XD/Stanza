# Generated by Django 4.2 on 2023-04-24 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_alter_dadosajucard_recarga_alter_dadosajucard_saldo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dadosajucard',
            name='data_planilha',
            field=models.DateField(blank=True, null=True),
        ),
    ]
