# Generated by Django 4.2 on 2023-06-20 18:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_minutas_previa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='minutas',
            name='previa',
        ),
    ]
