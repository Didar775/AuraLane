# Generated by Django 4.2.13 on 2024-11-30 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_userinstance_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinstance',
            name='phone_number',
            field=models.CharField(blank=True, max_length=11, null=True, unique=True, verbose_name='Номер телефона'),
        ),
    ]
