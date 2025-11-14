from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_farms_and_product_links(apps, schema_editor):
    """Create a basic Farm for each farmer with products and link their products.

    This keeps existing data working while introducing farm pages.
    """
    User = apps.get_model("users", "FarmerUser")
    Farm = apps.get_model("products", "Farm")
    Product = apps.get_model("products", "Product")

    # For each distinct farmer with at least one product, ensure a Farm exists.
    farmer_ids = (
        Product.objects.values_list("farmer_id", flat=True)
        .distinct()
        .exclude(farmer_id=None)
    )
    for farmer_id in farmer_ids:
        try:
            farmer = User.objects.get(pk=farmer_id)
        except User.DoesNotExist:
            continue
        farm, _ = Farm.objects.get_or_create(
            farmer=farmer,
            defaults={
                "name": f"{farmer.username}'s Farm" if farmer.username else "Farm",
                "slug": "",
                "location": farmer.location,
            },
        )
        # Let model's save handle slug generation on first save.
        if not farm.slug:
            farm.save()
        Product.objects.filter(farmer=farmer, farm__isnull=True).update(farm=farm)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_roles_and_profiles"),
        ("products", "0003_product_is_approved_product_is_reserved_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Farm",
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
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("banner_url", models.URLField(blank=True)),
                (
                    "branding_color",
                    models.CharField(
                        default="#15803d",
                        help_text="Hex or Tailwind-compatible color string used for farm theming.",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "farmer",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="farm",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="product",
            name="farm",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="products.farm",
            ),
        ),
        migrations.RunPython(backfill_farms_and_product_links, migrations.RunPython.noop),
    ]


