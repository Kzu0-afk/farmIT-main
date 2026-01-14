from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import FarmForm, ReviewForm
from ..models import Farm, Product, Review


@login_required
def my_farm(request: HttpRequest) -> HttpResponse:
    """Farmer-only management page for their virtual farm."""
    if not getattr(request.user, "is_farmer", False):
        return HttpResponse(status=403)

    farm, _created = Farm.objects.get_or_create(
        farmer=request.user,
        defaults={
            "name": f"{request.user.username}'s Farm" if request.user.username else "My Farm",
            "location": request.user.location,
        },
    )

    Product.objects.filter(farmer=request.user, farm__isnull=True).update(farm=farm)

    if request.method == "POST":
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            return redirect("my_farm")
    else:
        form = FarmForm(instance=farm)

    products = Product.objects.filter(farmer=request.user).order_by("-created_at")

    return render(
        request,
        "products/my_farm.html",
        {
            "farm": farm,
            "form": form,
            "products": products,
        },
    )


def farm_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Public-facing farm page with its approved products and reviews."""
    farm = get_object_or_404(Farm, slug=slug)
    products = Product.objects.filter(farm=farm, is_approved=True).only(
        "id",
        "product_name",
        "price",
        "quantity",
        "location",
        "photo_url",
        "created_at",
    )

    reviews_qs = Review.objects.filter(farm=farm).select_related("customer")
    aggregates = reviews_qs.aggregate(
        avg_rating=Avg("rating"),
        review_count=Count("id"),
    )

    review_form = None
    if request.user.is_authenticated and getattr(request.user, "is_customer", False):
        existing = reviews_qs.filter(customer=request.user).first()
        review_form = ReviewForm(instance=existing)

    return render(
        request,
        "products/farm_detail.html",
        {
            "farm": farm,
            "products": products,
            "reviews": reviews_qs,
            "avg_rating": aggregates["avg_rating"],
            "review_count": aggregates["review_count"],
            "review_form": review_form,
        },
    )


