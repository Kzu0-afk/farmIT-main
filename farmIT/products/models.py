from django.conf import settings
from django.db import models


class Product(models.Model):
    MODE_OF_PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('gcash', 'GCash'),
        ('bank', 'Bank Transfer'),
    ]

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
    )
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    mode_of_payment = models.CharField(
        max_length=20, choices=MODE_OF_PAYMENT_CHOICES, default='cash'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.product_name} ({self.quantity})"


