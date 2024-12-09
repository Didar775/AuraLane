from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone_number=None, username=None, password=None, **extra_fields):
        if not phone_number and not username:
            raise ValueError("Необходимо указать либо номер телефона, либо имя пользователя")
        if phone_number:
            extra_fields.setdefault('is_active', True)
            user = self.model(phone_number=phone_number, **extra_fields)
        else:
            user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(username=username, password=password, **extra_fields)


class UserInstance(AbstractUser):
    username = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Отображаемое имя"
    )
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="Номер телефона"
    )
    bonus = models.FloatField(
        default=0,
        verbose_name="Бонусы"
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def save(self, *args, **kwargs):
        if not self.username and self.phone_number:
            self.username = f"User-{self.phone_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username or self.phone_number


class UserProfile(models.Model):
    user = models.OneToOneField(
        UserInstance,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь"
    )
    profile_photo = models.ImageField(upload_to='profile_photos', blank=True, null=True, verbose_name="Фото профиля")
    additional_info = models.TextField(blank=True, null=True, verbose_name="Дополнительная информация")

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль для {self.user}"


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
