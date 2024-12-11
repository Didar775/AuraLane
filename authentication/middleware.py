import logging
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from users.models import UserInstance  # Импортируйте вашу кастомную модель пользователя

class TokenAuthMiddleware(MiddlewareMixin):
    """
    Middleware для извлечения токенов из cookies и аутентификации пользователя.
    """

    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                # Декодируем access_token
                payload = AccessToken(access_token)
                user_id = payload.get('user_id')

                # Получаем пользователя из базы данных
                user = UserInstance.objects.get(id=user_id)

                request.user = user
                logging.info(f"✅ Пользователь авторизован. ID: {user_id}")
            except UserInstance.DoesNotExist:
                logging.error(f"❌ Пользователь с ID {user_id} не найден.")
                request.user = AnonymousUser()
            except Exception as e:
                logging.error(f"❌ Ошибка аутентификации токена: {e}")
                request.user = AnonymousUser()
        else:
            logging.warning("⚠️ Нет токена в cookies")
            request.user = AnonymousUser()
