from django.db import migrations
from django.utils.text import slugify


def backfill_farm_slugs(apps, schema_editor):
    Farm = apps.get_model('products', 'Farm')
    for farm in Farm.objects.filter(slug=''):
        base = slugify(farm.name or getattr(farm.farmer, 'username', '') or f'farm-{farm.farmer_id}')
        slug = base or f'farm-{farm.farmer_id}'
        counter = 1
        while Farm.objects.exclude(pk=farm.pk).filter(slug=slug).exists():
            counter += 1
            slug = f"{base}-{counter}"
        farm.slug = slug
        farm.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_farm_latitude_farm_longitude_address_deliveryrequest_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_farm_slugs, migrations.RunPython.noop),
    ]


