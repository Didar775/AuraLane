# Generated by Django 4.2.13 on 2024-11-17 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0001_initial'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='sale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sales.sale'),
        ),
        migrations.AddField(
            model_name='item',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='items', to='catalog.tag'),
        ),
        migrations.AddField(
            model_name='favoriteitem',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='catalog.item', verbose_name='товар'),
        ),
        migrations.AddField(
            model_name='favoriteitem',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        migrations.AddConstraint(
            model_name='favoriteitem',
            constraint=models.UniqueConstraint(fields=('item', 'user'), name='unique_item_to_add'),
        ),
    ]
