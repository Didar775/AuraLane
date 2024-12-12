from django.urls import path
from .views import CartOrderView

app_name = 'sales'

urlpatterns = [
    path('cart-order/', CartOrderView.as_view(), name='cart_order'),
    path("shopping-history/", CartOrderView.as_view(), {"action": "history"}, name="shopping_history"),

]
