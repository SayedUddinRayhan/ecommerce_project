# Generated by Django 5.1.5 on 2025-02-26 05:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_cart_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
