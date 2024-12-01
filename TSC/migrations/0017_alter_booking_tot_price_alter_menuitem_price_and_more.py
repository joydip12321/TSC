# Generated by Django 5.1.2 on 2024-12-01 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TSC', '0016_alter_orders_order_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='tot_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
        migrations.AlterField(
            model_name='orders',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='room',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]