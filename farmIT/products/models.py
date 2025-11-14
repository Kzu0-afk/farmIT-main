from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Farm(models.Model):
    """Virtual farm page owned by a single farmer user."""

    farmer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farm",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    banner_url = models.URLField(blank=True)
    branding_color = models.CharField(
        max_length=32,
        default="#15803d",  # Tailwind green-700
        help_text="Hex or Tailwind-compatible color string used for farm theming.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate slug from name/username if not provided, ensure uniqueness in a simple way.
        if not self.slug:
            base = slugify(self.name or self.farmer.username)
            slug = base or f"farm-{self.farmer_id}"
            counter = 1
            Model = self.__class__
            while Model.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                counter += 1
                slug = f"{base}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)


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
    # New link to farm (Phase 3). Kept nullable for backward compatibility.
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True,
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

    # Moderation & reservation
    is_approved = models.BooleanField(default=True)
    is_reserved = models.BooleanField(default=False)
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserved_products',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.product_name} ({self.quantity})"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('interested', 'Interested'),
        ('reserved', 'Reserved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='interested')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['product', 'buyer'])]

    def __str__(self) -> str:
        return f"{self.buyer} -> {self.product} [{self.status}]"

