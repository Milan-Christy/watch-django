# Generated by Django 4.1.5 on 2023-01-31 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0007_cartitem_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='max_use',
            field=models.IntegerField(default=100),
        ),
    ]
