from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'farmer',
        'price',
        'quantity',
        'location',
        'mode_of_payment',
        'created_at',
    )
    search_fields = ('product_name', 'description', 'location', 'farmer__username')
    list_filter = ('mode_of_payment',)


