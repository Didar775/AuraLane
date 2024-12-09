from django.db import models
from django.db.models import Avg

from users.models import UserInstance


class Category(models.Model):
    name = models.CharField(max_length=50, blank=True)
    updated = models.DateTimeField(blank=True, null=True)
    archived = models.BooleanField(default=False)
    href = models.URLField(blank=True, null=True, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=40)
    is_brand = models.BooleanField(default=False)
    is_displayed = models.BooleanField(default=False)
    image = models.ImageField(upload_to='brands', blank=True, null=True)

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return 'id - %s, name - %s' % (self.pk, self.name)


class Item(models.Model):
    name = models.CharField(max_length=40, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    buy_price = models.FloatField(default=0, blank=True)
    sale_price = models.FloatField(default=0, blank=True)
    min_price = models.FloatField(default=0, blank=True)
    weight = models.FloatField(default=0, blank=True)
    href = models.URLField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    in_stock = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='items', blank=True)

    sale = models.ForeignKey('sales.Sale', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    @property
    def brand(self):
        if not hasattr(self, 'tags'):
            return ''
        brand = self.tags.filter(is_brand=True).first()
        return getattr(brand, 'name', '')

    @property
    def average_rating(self):
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def total_reviews(self):
        return self.ratings.count()


class ItemPhoto(models.Model):
    STATUSES = [
        ('main', 'MAIN'),
        ('scroll', 'SCROLL')
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    filename = models.CharField(max_length=100, null=True, blank=True)
    download_href = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default='scroll')
    photo = models.ImageField(upload_to='item_photos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Фотография товара'
        verbose_name_plural = 'Фотография товаров'

    def __str__(self):
        return f'{self.item.name} - {self.photo}'


class FavoriteItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True, verbose_name='товар',
                             related_name='favorites')
    user = models.ForeignKey(UserInstance, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True,
                             verbose_name='пользователь')

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'
        constraints = [
            models.UniqueConstraint(
                fields=['item', 'user'],
                name='unique_item_to_add'
            )
        ]


class Review(models.Model):
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pros = models.TextField(null=True, blank=True)
    cons = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    author = models.ForeignKey(UserInstance, on_delete=models.CASCADE, related_name='ratings', null=True, blank=True, )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ratings', null=True, blank=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f"{self.author.username} - {self.rating}"
