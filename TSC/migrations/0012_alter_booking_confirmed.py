# Generated by Django 5.1.2 on 2024-10-25 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TSC', '0011_rename_ref_national_id_userprofile_national_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='confirmed',
            field=models.IntegerField(default=0),
        ),
    ]
