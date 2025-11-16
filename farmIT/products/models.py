from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

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
    # Optional coordinates for map and delivery calculations (Phase 3).
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Latitude in decimal degrees (e.g. 14.599512).",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude in decimal degrees (e.g. 120.984222).",
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


class Review(models.Model):
    """Customer review of a farm (1–5 star rating plus optional comment)."""

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farm_reviews",
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["farm", "customer"],
                name="unique_review_per_customer_per_farm",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Review<{self.customer} -> {self.farm} ({self.rating})>"


class Address(models.Model):
    """Customer address for delivery planning (with optional coordinates)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    label = models.CharField(
        max_length=100,
        help_text="Short label like 'Home' or 'Restaurant'.",
    )
    line1 = models.CharField(max_length=255)
    barangay = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=64, default="Philippines")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Latitude in decimal degrees (optional).",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude in decimal degrees (optional).",
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.label} ({self.user})"

    @property
    def full_address(self) -> str:
        parts = [self.line1]
        if self.barangay:
            parts.append(self.barangay)
        if self.city:
            parts.append(self.city)
        if self.province:
            parts.append(self.province)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

    def save(self, *args, **kwargs):
        # Ensure only one default address per user.
        if self.is_default and self.user_id:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class DeliveryRequest(models.Model):
    """Delivery quote/request from a customer for a farm order."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUOTED = "quoted", "Quoted"
        ACCEPTED = "accepted", "Accepted"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="delivery_requests",
    )
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="delivery_requests",
    )
    # We keep a snapshot of the pickup address text so historical records
    # remain stable even if the farm location changes.
    pickup_address_text = models.CharField(max_length=255)
    dropoff_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name="delivery_requests",
    )
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    eta_minutes = models.PositiveIntegerField()
    quoted_fee = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["farm", "customer"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Delivery<{self.customer} -> {self.farm} {self.distance_km}km>"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance between two points in kilometers."""

    # Radius of Earth in kilometers.
    r = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def estimate_distance_and_fee(
    farm: Farm,
    address: Address,
    base_fee: Decimal | None = None,
    per_km_fee: Decimal | None = None,
) -> tuple[Decimal, int, Decimal]:
    """Estimate distance, ETA and delivery fee using local coordinates only.

    This keeps all computation server-side with no external API calls,
    respecting the no-mock-data rule by relying on real coordinates when provided.
    """

    if farm.latitude is None or farm.longitude is None:
        raise ValueError("Farm must have latitude and longitude set for delivery estimation.")
    if address.latitude is None or address.longitude is None:
        raise ValueError("Address must have latitude and longitude set for delivery estimation.")

    lat1 = float(farm.latitude)
    lon1 = float(farm.longitude)
    lat2 = float(address.latitude)
    lon2 = float(address.longitude)

    distance_km = Decimal(str(round(_haversine_km(lat1, lon1, lat2, lon2), 2)))

    # Simple ETA: assume average speed of ~25 km/h including city traffic.
    avg_speed_kmh = Decimal("25")
    eta_hours = distance_km / avg_speed_kmh if distance_km > 0 else Decimal("0")
    eta_minutes = int((eta_hours * Decimal("60")).quantize(Decimal("1")))

    base = base_fee if base_fee is not None else Decimal("50")
    per_km = per_km_fee if per_km_fee is not None else Decimal("10")
    quoted_fee = (base + (distance_km * per_km)).quantize(Decimal("1"))

    return distance_km, max(eta_minutes, 1), quoted_fee

