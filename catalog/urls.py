from django.urls import path
from .views import (
    ItemListView, ItemDetailView, toggle_favorite, submit_review, home_view,
    CategoryListView
)

app_name = 'catalog'

urlpatterns = [
    path('', home_view, name='home'),
    path('catalog/', CategoryListView.as_view(), name='catalog-items'),
    path('product/<int:pk>/', ItemDetailView.as_view(), name='item_detail')
]
