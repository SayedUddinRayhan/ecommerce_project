# Generated by Django 5.1.5 on 2025-02-16 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_variation_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='requires_color',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='requires_size',
            field=models.BooleanField(default=False),
        ),
    ]
