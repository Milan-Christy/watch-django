# Generated by Django 4.1.5 on 2023-02-01 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_product_is_offer_product_offer_product_offered_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='offered_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
