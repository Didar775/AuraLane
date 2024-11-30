from rest_framework.test import APITestCase
from rest_framework import status
from users.models import UserInstance
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.phone_number = "1234567890"
        self.otp_code = "123456"
        self.generate_otp_url = "/api/auth/generate-otp/"
        self.verify_otp_url = "/api/auth/verify-otp/"
        cache.set(f"otp:{self.phone_number}", self.otp_code, timeout=300)

    def test_generate_otp(self):
        response = self.client.post(self.generate_otp_url, {"phone_number": self.phone_number})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'OTP успешно сгенерирован')

    def test_verify_otp_and_register_user(self):
        response = self.client.post(self.verify_otp_url, {"phone_number": self.phone_number, "otp": self.otp_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(UserInstance.objects.filter(phone_number=self.phone_number).exists())

    def test_verify_otp_for_existing_user(self):
        UserInstance.objects.create(phone_number=self.phone_number)
        response = self.client.post(self.verify_otp_url, {"phone_number": self.phone_number, "otp": self.otp_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_verify_otp_invalid_code(self):
        response = self.client.post(self.verify_otp_url, {"phone_number": self.phone_number, "otp": "000000"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Неверный OTP')

    def test_generate_otp_without_phone_number(self):
        response = self.client.post(self.generate_otp_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Номер телефона обязателен')

    def test_verify_otp_without_otp(self):
        response = self.client.post(self.verify_otp_url, {"phone_number": self.phone_number})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Номер телефона и код обязательны')

    def test_verify_otp_with_expired_code(self):
        cache.delete(f"otp:{self.phone_number}")
        response = self.client.post(self.verify_otp_url, {"phone_number": self.phone_number, "otp": self.otp_code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'OTP истёк или недействителен')
