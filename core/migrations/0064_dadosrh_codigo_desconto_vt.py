# Generated by Django 4.2 on 2023-05-22 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0063_dadosrh_matricula'),
    ]

    operations = [
        migrations.AddField(
            model_name='dadosrh',
            name='codigo_desconto_vt',
            field=models.CharField(max_length=100, null=True),
        ),
    ]