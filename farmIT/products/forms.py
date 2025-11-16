from django import forms

from .models import Address, Farm, Product, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "product_name",
            "price",
            "quantity",
            "description",
            "photo_url",
            "location",
            "mode_of_payment",
        )


class FarmForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind-friendly classes in one place instead of custom template filters.
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                "focus:ring-green-600 focus:border-transparent",
            )

    class Meta:
        model = Farm
        fields = (
            "name",
            "description",
            "location",
            "banner_url",
            "branding_color",
            "latitude",
            "longitude",
        )


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                "focus:ring-green-600 focus:border-transparent text-sm",
            )

    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                "focus:ring-green-600 focus:border-transparent text-sm",
            )

    class Meta:
        model = Address
        fields = (
            "label",
            "line1",
            "barangay",
            "city",
            "province",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "is_default",
        )

