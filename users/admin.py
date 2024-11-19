from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserInstance, Address


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone_number', 'email', 'bonus', 'is_staff')
    search_fields = ('username', 'phone_number', 'email')
    ordering = ('-date_joined',)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'home_number')
    search_fields = ('city', 'street')
    list_filter = ('city',)


admin.site.register(UserInstance, CustomUserAdmin)
admin.site.register(Address, AddressAdmin)
