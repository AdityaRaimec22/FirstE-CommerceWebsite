# Generated by Django 4.2 on 2023-07-28 05:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_order_current_time_alter_order_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='current_Time',
        ),
    ]
