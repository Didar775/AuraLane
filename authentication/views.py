import requests
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404, render
from random import randint

from trendhive.settings import get_env_variable
from users.models import UserInstance
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.conf import settings

def otp_auth_view(request):
    return render(request, 'authentication.html')


def send_sms(url, data, headers):
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            uid = response.json().get('uid')
            return Response({'uid': uid}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send SMS', 'details': response.text}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({'error': 'Network error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateOTPView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({'error': 'Номер телефона обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        url = f"{get_env_variable('SMS_URL')}/api/create/"
        headers = {
            'Authorization': f"Bearer {get_env_variable('SMS_TOKEN')}",
            'Content-Type': 'application/json'
        }
        data = {
            'phone_number': phone_number
        }
        response = send_sms(url, data, headers)
        if response.status_code not in [200,201]:
            return Response({"error": "Can't send message", "status_code": response.status_code}, status=response.status_code)
        print(response.data)
        cache.set(str(phone_number), response.data.get("uid"), timeout=300)

        return Response({'message': 'OTP успешно сгенерирован'}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        uid = cache.get(str(phone_number))
        code = request.data.get('code')
        if not phone_number or not uid:
            return Response({'error': 'Номер телефона и код обязательны'}, status=status.HTTP_400_BAD_REQUEST)

        url = f"{get_env_variable('SMS_URL')}/api/verify/"
        headers = {
            'Authorization': f"Bearer {get_env_variable('SMS_TOKEN')}",
            'Content-Type': 'application/json'
        }
        data = {
            'uid': uid,
            'code': code
        }
        response = send_sms(url, data, headers)
        if response.status_code not in [200, 201]:
            print(response.data)
            return Response({"error": "Invalid code!", "status_code": response.status_code}, status=response.status_code)

        cache.delete(phone_number)

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
