from django.urls import path
from .views import profile_page
app_name = 'users'

urlpatterns = [
    path('', profile_page, name='profile_page'),
]
