# Generated by Django 4.2.15 on 2024-09-07 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_leftoverproduct_restock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leftoverproduct',
            name='restock',
            field=models.BooleanField(default=False),
        ),
    ]