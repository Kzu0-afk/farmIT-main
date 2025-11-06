from django.contrib.auth.models import AbstractUser
from django.db import models


class FarmerUser(AbstractUser):
    """Custom user model for farmers with additional profile fields.

    We keep the default username for simplicity and add unique email,
    location and contact number fields to match the MVP schema.
    """

    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return self.username or self.email


