# Generated by Django 4.2 on 2023-04-19 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_indeterminados'),
    ]

    operations = [
        migrations.AddField(
            model_name='indeterminados',
            name='data_prev_final',
            field=models.DateField(blank=True, null=True),
        ),
    ]
