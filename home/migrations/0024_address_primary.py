# Generated by Django 4.2 on 2023-08-06 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_delete_orderupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='primary',
            field=models.BooleanField(default=False),
        ),
    ]
