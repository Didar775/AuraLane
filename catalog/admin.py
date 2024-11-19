from django.contrib import admin
from .models import Category, Tag, Item, ItemPhoto, FavoriteItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated', 'archived')
    list_filter = ('archived',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_brand', 'is_displayed')
    list_filter = ('is_brand', 'is_displayed')
    search_fields = ('name',)


class ItemPhotoInline(admin.TabularInline):
    model = ItemPhoto
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'buy_price', 'sale_price', 'in_stock')
    list_filter = ('category', 'in_stock')
    search_fields = ('name', 'code')
    inlines = [ItemPhotoInline]


@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'user')
    list_filter = ('user',)
    search_fields = ('item__name', 'user__username')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('item', 'author', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('item__name', 'author__username')
