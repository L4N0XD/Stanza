# Generated by Django 4.2 on 2023-05-10 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_rename_data_emissão_dadoscomercial_data_emissao'),
    ]

    operations = [
        migrations.AddField(
            model_name='dadoscomercial',
            name='id_value',
            field=models.AutoField(default=0, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='dadoscomercial',
            name='par',
            field=models.CharField(max_length=10),
        ),
    ]
