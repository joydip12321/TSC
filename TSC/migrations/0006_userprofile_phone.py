# Generated by Django 5.1.1 on 2024-10-18 16:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("TSC", "0005_alter_orders_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="phone",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
