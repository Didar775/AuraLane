from decimal import Decimal

from django.db import models

from api.validators import PERCENTAGE_VALIDATOR
from catalog.models import Item
from users.models import UserInstance, Address


class Sale(models.Model):
    title = models.CharField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    photo = models.ImageField(upload_to='sale_photo/', blank=True, null=True, verbose_name='Фотография')
    percent = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        default=Decimal(0),
        validators=PERCENTAGE_VALIDATOR
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ('pk',)
        indexes = [
            models.Index(fields=['title', 'description', 'short_description']),
        ]

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUSES = [
        ('new', 'NEW'),
        ('canceled', 'CANCELED'),
        ('completed', 'COMPLETED'),
    ]

    user = models.ForeignKey(UserInstance, on_delete=models.CASCADE, related_name='orders', blank=True, null=True,
                             verbose_name='пользователь')
    status = models.CharField(choices=STATUSES, max_length=50, default='new', verbose_name='статус доставки')

    delivery_date = models.DateTimeField(blank=True, null=True, verbose_name='дата доставки')
    delivery_address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True,
                                         verbose_name='адрес доставки')

    delivery_price = models.IntegerField(blank=True, null=True, verbose_name='цена доставки', default=2000)
    discount_price = models.FloatField(blank=True, null=True, verbose_name='скидка', default=0)
    bonus_price = models.FloatField(blank=True, null=True, verbose_name='начисленный бонус', default=0)
    use_bonus = models.BooleanField(blank=True, null=True, verbose_name='использовать бонус', default=False)

    transaction_id = models.CharField(max_length=255, default='', null=True, blank=True)
    verified = models.BooleanField(verbose_name='Подтерждено от TipTopPayments', default=False)
    error_code = models.CharField(verbose_name='Код статуса', default='200', max_length=10)
    error_text = models.TextField(verbose_name='Текст ошибки', default='', null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-delivery_date']

    @property
    def cart_prices(self):
        return sum(cart.quantity * cart.item.sale_price for cart in self.carts.all())

    @property
    def total_price(self):
        if self.status == 'new':
            self.bonus_price = self.user.bonus if self.use_bonus else 0
            self.save()

        return self.cart_prices + self.delivery_price - self.discount_price - self.bonus_price


class Cart(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True, verbose_name='товар')
    quantity = models.IntegerField(default=1, blank=True, verbose_name='количество')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='carts', blank=True, null=True,
                              verbose_name='номер заказа')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.item.name} - {self.quantity} штук'

