from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404, render
from random import randint
from users.models import UserInstance
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


def otp_auth_view(request):
    return render(request, 'authentication.html')


class GenerateOTPView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({'error': 'Номер телефона обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = randint(100000, 999999)
        cache.set(f"otp:{phone_number}", otp_code, timeout=300)
        print(f"OTP для {phone_number}: {otp_code}")

        return Response({'message': 'OTP успешно сгенерирован'}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('otp')

        if not phone_number or not otp_code:
            return Response({'error': 'Номер телефона и код обязательны'}, status=status.HTTP_400_BAD_REQUEST)

        saved_otp = cache.get(f"otp:{phone_number}")
        if not saved_otp:
            return Response({'error': 'OTP истёк или недействителен'}, status=status.HTTP_400_BAD_REQUEST)

        if str(saved_otp) != str(otp_code):
            return Response({'error': 'Неверный OTP'}, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(f"otp:{phone_number}")

        user, created = UserInstance.objects.get_or_create(phone_number=phone_number)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({'message': 'Вы успешно авторизовались'}, status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite='Lax', max_age=60 * 15)
        response.set_cookie(key='refresh_token', value=str(refresh), httponly=True, secure=True, samesite='Strict', max_age=60 * 60 * 24 * 7)
        return response


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token отсутствует'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            new_access_token = str(refresh.access_token)
            response = Response({'message': 'Токен обновлён'}, status=status.HTTP_200_OK)
            response.set_cookie(key='access_token', value=new_access_token, httponly=True, secure=True, samesite='Lax', max_age=60 * 15)
            return response
        except Exception:
            return Response({'error': 'Refresh token недействителен'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token отсутствует'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            response = Response({'message': 'Вы успешно вышли'}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception:
            return Response({'error': 'Невозможно выполнить выход'}, status=status.HTTP_400_BAD_REQUEST)
