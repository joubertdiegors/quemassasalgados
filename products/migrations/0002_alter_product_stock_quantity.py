# Generated by Django 4.2.15 on 2024-08-25 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.IntegerField(default=0),
        ),
    ]
