# Generated by Django 4.1.5 on 2023-01-10 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cartitem_variations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='cart_id',
        ),
    ]
