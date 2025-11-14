from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import FarmerUser


class FarmerUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=FarmerUser.Roles.choices,
        widget=forms.RadioSelect,
        label="I want to use FarmIT as a",
    )

    class Meta(UserCreationForm.Meta):
        model = FarmerUser
        fields = (
            "username",
            "email",
            "location",
            "contact_number",
            "role",
        )


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerUser
        fields = (
            "email",
            "location",
            "contact_number",
        )


