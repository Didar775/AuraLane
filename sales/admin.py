from django.contrib import admin
from .models import Sale, Cart, Order


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'amount', 'percent')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'description')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity')
    search_fields = ('item__name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'delivery_date', 'total_price', 'verified')
    list_filter = ('status', 'verified')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('cart_prices', 'total_price')

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = 'Total Price'
