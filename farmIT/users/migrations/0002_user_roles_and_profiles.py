from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="farmeruser",
            name="role",
            field=models.CharField(
                choices=[("farmer", "Farmer"), ("customer", "Customer")],
                default="farmer",
                help_text="Determines whether this account behaves as a Farmer or Customer.",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("preferences_json", models.JSONField(blank=True, default=dict)),
                ("avatar_url", models.URLField(blank=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FarmerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bio", models.TextField(blank=True)),
                ("address", models.CharField(blank=True, max_length=255)),
                (
                    "verification_status",
                    models.CharField(
                        default="unverified",
                        help_text="Simple flag for future KYC/verification flows.",
                        max_length=32,
                    ),
                ),
                ("avatar_url", models.URLField(blank=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="farmer_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]


