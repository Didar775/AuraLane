from django.urls import path
from .views import CartOrderView

app_name = 'sales'

urlpatterns = [
    path('cart-order/', CartOrderView.as_view(), name='cart_order'),
]
