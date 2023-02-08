# Generated by Django 4.1.5 on 2023-01-24 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Placed', 'Placed'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned')], default='Placed', max_length=10),
        ),
    ]
