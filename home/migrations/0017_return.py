# Generated by Django 4.2 on 2023-07-28 02:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0016_order_user_orderupdate_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Return',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
                ('phone', models.CharField(default='', max_length=70)),
                ('email', models.CharField(default='', max_length=100)),
                ('returnId', models.CharField(default='', max_length=70)),
                ('desc', models.CharField(default='', max_length=500)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
