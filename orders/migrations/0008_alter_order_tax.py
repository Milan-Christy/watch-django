# Generated by Django 4.1.5 on 2023-02-07 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_alter_order_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.FloatField(null=True),
        ),
    ]
