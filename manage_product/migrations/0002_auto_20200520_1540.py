# Generated by Django 3.0.6 on 2020-05-20 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tag',
            field=models.ManyToManyField(blank=True, to='manage_product.Tag'),
        ),
    ]
