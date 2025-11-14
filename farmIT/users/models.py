from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class FarmerUser(AbstractUser):
    """Custom user model that supports both farmers and customers.

    We extend the default Django user with:
    - unique email field
    - basic contact/location fields
    - a simple `role` flag that drives permissions and redirects
    """

    class Roles(models.TextChoices):
        FARMER = "farmer", "Farmer"
        CUSTOMER = "customer", "Customer"

    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.FARMER,
        help_text="Determines whether this account behaves as a Farmer or Customer.",
    )

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.username or self.email

    @property
    def is_farmer(self) -> bool:
        return self.role == self.Roles.FARMER

    @property
    def is_customer(self) -> bool:
        return self.role == self.Roles.CUSTOMER


class FarmerProfile(models.Model):
    """Optional extended profile data for farmer accounts.

    Kept minimal for now but ready for future expansion (branding, documents, etc.).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farmer_profile",
    )
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    verification_status = models.CharField(
        max_length=32,
        default="unverified",
        help_text="Simple flag for future KYC/verification flows.",
    )
    avatar_url = models.URLField(blank=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"FarmerProfile<{self.user.username}>"


class CustomerProfile(models.Model):
    """Optional extended profile data for customers.

    Stores preferences in a JSON blob for future personalization features.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    preferences_json = models.JSONField(default=dict, blank=True)
    avatar_url = models.URLField(blank=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"CustomerProfile<{self.user.username}>"

