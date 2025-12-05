from django import forms

from .models import Address, Farm, Product, Review


class ProductForm(forms.ModelForm):
    # Optional image URL (kept for backward compatibility / manual URLs)
    photo_url = forms.URLField(
        required=False,
        label="Image URL (optional)",
        widget=forms.URLInput(attrs={"placeholder": "https://..."}),
    )
    # Optional file upload that will be stored in Supabase Storage.
    # When provided, it will override any manual photo_url entered.
    image_file = forms.FileField(
        required=False,
        label="Product Image Upload",
        help_text="Upload a product image to Supabase Storage (optional).",
    )

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
            "image_file",
        )

    def clean(self):
        cleaned = super().clean()
        image_file = cleaned.get("image_file")
        photo_url = cleaned.get("photo_url")

        # If a file is provided, ignore any photo_url validation noise and let upload overwrite.
        if image_file:
            if "photo_url" in self._errors:
                self._errors.pop("photo_url", None)
            cleaned["photo_url"] = ""  # will be set to uploaded URL in the view
        else:
            # Normalize URL if provided
            if photo_url:
                cleaned["photo_url"] = photo_url.strip()
        return cleaned


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

