# Generated by Django 5.1.5 on 2025-03-01 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
        ('store', '0006_remove_orderitem_order_remove_ordertransaction_order_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='variation',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='variations',
            field=models.ManyToManyField(blank=True, to='store.variation'),
        ),
    ]
