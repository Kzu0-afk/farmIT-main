from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "placeholder": "Type your message…",
                "class": "block w-full px-3 py-2 border border-gray-300 rounded-lg "
                "focus:ring-2 focus:ring-green-600 focus:border-transparent text-sm",
            }
        ),
        max_length=1000,
        label="",
    )

    class Meta:
        model = Message
        fields = ("body",)


