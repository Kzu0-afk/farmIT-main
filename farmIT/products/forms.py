from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'product_name',
            'price',
            'quantity',
            'description',
            'photo_url',
            'location',
            'mode_of_payment',
        )


