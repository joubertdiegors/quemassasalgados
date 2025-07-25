# Generated by Django 4.2.15 on 2025-04-14 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_rename_is_active_product_use_in_production_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='show_on_website',
            field=models.BooleanField(default=False),
        ),
    ]
