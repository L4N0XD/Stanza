# Generated by Django 4.2 on 2023-05-09 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_dadosvt_numero_endereco'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadosvt',
            name='cpf',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
