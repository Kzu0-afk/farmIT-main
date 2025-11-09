from django.contrib import admin

from .models import Product, Transaction


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'farmer',
        'price',
        'quantity',
        'location',
        'mode_of_payment',
        'is_approved',
        'is_reserved',
        'reserved_by',
        'created_at',
    )
    search_fields = ('product_name', 'description', 'location', 'farmer__username')
    list_filter = ('mode_of_payment', 'is_approved', 'is_reserved')
    list_editable = ('is_approved',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'buyer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product__product_name', 'buyer__username')


