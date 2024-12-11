from django.urls import path
from .views import (
    ItemListView, ItemDetailView, toggle_favorite, submit_review, home_view,
   FavoriteItemView
)

app_name = 'catalog'

urlpatterns = [
    path('', home_view, name='home'),
    path('catalog/', ItemListView.as_view(), name='catalog-items'),
    path('product/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('item/<int:item_id>/review/', submit_review, name='submit_review'),
    path('toggle-favorite/<int:product_id>/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', FavoriteItemView.as_view(), name='favorites'),
]
