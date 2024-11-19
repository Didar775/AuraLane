from django.contrib.auth.models import AbstractUser
from django.db import models


class UserInstance(AbstractUser):
    username = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    bonus = models.FloatField(default=0)
    profile_photo = models.ImageField(upload_to='profile_photos')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.phone_number


class Address(models.Model):
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='город')
    street = models.CharField(max_length=100, blank=True, null=True, verbose_name='улица/микрорайон')
    home_number = models.IntegerField(blank=True, null=True, verbose_name='дом/строение')
    additional_info = models.TextField(blank=True, null=True, verbose_name='дополнительные инструкция курьеру')
    user = models.ForeignKey(UserInstance, on_delete=models.CASCADE, null=True, blank=True, verbose_name='пользователь',
                             related_name='addresses')

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'

    def __str__(self):
        return f"{self.city}, {self.street}"
