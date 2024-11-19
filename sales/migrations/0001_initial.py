# Generated by Django 4.2.13 on 2024-11-17 10:54

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('short_description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('amount', models.FloatField(blank=True, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='sale_photo/', verbose_name='Фотография')),
                ('percent', models.DecimalField(decimal_places=0, default=Decimal('0'), max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Продажа',
                'verbose_name_plural': 'Продажи',
                'ordering': ('pk',),
                'indexes': [models.Index(fields=['title', 'description', 'short_description'], name='sales_sale_title_2debdc_idx')],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'NEW'), ('canceled', 'CANCELED'), ('completed', 'COMPLETED')], default='new', max_length=50, verbose_name='статус доставки')),
                ('delivery_date', models.DateTimeField(blank=True, null=True, verbose_name='дата доставки')),
                ('delivery_price', models.IntegerField(blank=True, default=2000, null=True, verbose_name='цена доставки')),
                ('discount_price', models.FloatField(blank=True, default=0, null=True, verbose_name='скидка')),
                ('bonus_price', models.FloatField(blank=True, default=0, null=True, verbose_name='начисленный бонус')),
                ('use_bonus', models.BooleanField(blank=True, default=False, null=True, verbose_name='использовать бонус')),
                ('transaction_id', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('verified', models.BooleanField(default=False, verbose_name='Подтерждено от TipTopPayments')),
                ('error_code', models.CharField(default='200', max_length=10, verbose_name='Код статуса')),
                ('error_text', models.TextField(blank=True, default='', null=True, verbose_name='Текст ошибки')),
                ('delivery_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.address', verbose_name='адрес доставки')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
                'ordering': ['-delivery_date'],
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, default=1, verbose_name='количество')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.item', verbose_name='товар')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины',
            },
        ),
    ]
