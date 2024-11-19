from django.urls import path
from .views import (
    ItemListView, ItemDetailView, toggle_favorite, submit_review, home_view, items_by_category,
    catalog_list
)

app_name = 'catalog'

urlpatterns = [
    path('', home_view, name='home'),
    path('catalog/', catalog_list, name='catalog_list'),
    path('items/<int:category_id>/', items_by_category, name='items_by_category'),
    path('product/', ItemListView.as_view(), name='item_list'),
    path('<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('favorite/<int:item_id>/', toggle_favorite, name='toggle_favorite'),
    path('review/<int:item_id>/', submit_review, name='submit_review'),
]
