from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Prefetch, Q
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from users.models import FarmerUser

from .forms import AddressForm, FarmForm, ProductForm, ReviewForm
from .models import (
    Address,
    DeliveryRequest,
    Farm,
    Product,
    Review,
    Transaction,
    estimate_distance_and_fee,
)


def landing_page(request: HttpRequest) -> HttpResponse:
    """Landing page with hero section and info about FarmIT.

    For logged-in customers, we treat the marketplace as their primary home.
    """
    user = request.user
    if getattr(user, "is_authenticated", False) and getattr(user, "is_customer", False):
        return redirect("product_list")
    return render(request, "products/landing_page.html")


def product_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    products = Product.objects.filter(is_approved=True)
    if query:
        products = products.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query)
        )
    if location:
        products = products.filter(location__icontains=location)
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Marketplace highlights: top farms by number of approved products.
    # Keep SQL simple for broad DB compatibility.
    highlight_farms = (
        Farm.objects.filter(products__is_approved=True)
        .exclude(slug="")
        .annotate(active_products=Count("products", distinct=True))
        .order_by("-active_products", "name")
        .prefetch_related(
            Prefetch(
                "products",
                queryset=Product.objects.filter(is_approved=True).order_by("-created_at"),
                to_attr="top_products",
            )
        )[:6]
    )

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'query': query,
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            'highlight_farms': highlight_farms,
        },
    )


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    # Only show unapproved products to their owners or staff
    if not product.is_approved and not (request.user.is_authenticated and (request.user == product.farmer or request.user.is_staff)):
        return HttpResponseForbidden('This product is not available.')

    interests = []
    if request.user.is_authenticated and request.user == product.farmer:
        interests = list(Transaction.objects.filter(product=product, status='interested').select_related('buyer'))

    return render(request, 'products/product_detail.html', {
        'product': product,
        'interests': interests,
    })


@login_required
def product_create(request: HttpRequest) -> HttpResponse:
    # Only farmer accounts are allowed to create listings.
    if not getattr(request.user, "is_farmer", False):
        return HttpResponseForbidden("Only farmer accounts can create product listings.")

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            # Ensure product is associated with this farmer's farm if available.
            farm = getattr(request.user, "farm", None)
            if farm:
                product.farm = farm
            product.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})


@login_required
def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    if not getattr(request.user, "is_farmer", False):
        return HttpResponseForbidden("Only farmer accounts can manage product listings.")

    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form})


@login_required
def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    if not getattr(request.user, "is_farmer", False):
        return HttpResponseForbidden("Only farmer accounts can manage product listings.")

    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})


@login_required
def create_interest(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk, is_approved=True)
    if product.farmer_id == request.user.id:
        return HttpResponseForbidden('You cannot register interest in your own product.')
    # Prevent duplicate interests
    exists = Transaction.objects.filter(product=product, buyer=request.user, status='interested').exists()
    if not exists:
        Transaction.objects.create(product=product, buyer=request.user, status='interested')
    return redirect('product_detail', pk=pk)


@login_required
def reserve_transaction(request: HttpRequest, tx_id: int) -> HttpResponse:
    tx = get_object_or_404(Transaction, pk=tx_id, status='interested')
    product = tx.product
    if request.user != product.farmer and not request.user.is_staff:
        return HttpResponseForbidden('Not allowed')
    product.is_reserved = True
    product.reserved_by = tx.buyer
    product.save(update_fields=['is_reserved', 'reserved_by'])
    tx.status = 'reserved'
    tx.save(update_fields=['status'])
    return redirect('product_detail', pk=product.pk)


@staff_member_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    pending_products = Product.objects.filter(is_approved=False).count()
    reserved_products = Product.objects.filter(is_reserved=True).count()
    total_users = Product._meta.apps.get_model('users', 'FarmerUser').objects.count()
    total_interests = Transaction.objects.filter(status='interested').count()

    # Top locations (simple aggregate)
    from django.db.models import Count
    top_locations = (
        Product.objects.values('location')
        .exclude(location='')
        .annotate(c=Count('id'))
        .order_by('-c')[:5]
    )

    return render(request, 'admin/dashboard.html', {
        'total_products': total_products,
        'approved_products': approved_products,
        'pending_products': pending_products,
        'reserved_products': reserved_products,
        'total_users': total_users,
        'total_interests': total_interests,
        'top_locations': top_locations,
    })


@login_required
def my_farm(request: HttpRequest) -> HttpResponse:
    """Farmer-only management page for their virtual farm."""
    if not getattr(request.user, "is_farmer", False):
        return HttpResponseForbidden("Only farmer accounts can access farm management.")

    farm, _created = Farm.objects.get_or_create(
        farmer=request.user,
        defaults={
            "name": f"{request.user.username}'s Farm" if request.user.username else "My Farm",
            "location": request.user.location,
        },
    )

    # Keep products in sync with this farm reference.
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
    products = Product.objects.filter(farm=farm, is_approved=True)

    reviews_qs = Review.objects.filter(farm=farm).select_related("customer")
    aggregates = reviews_qs.aggregate(
        avg_rating=Avg("rating"),
        review_count=Count("id"),
    )

    review_form = None
    if request.user.is_authenticated and getattr(request.user, "is_customer", False):
        # Preload existing review if present so customers can update their rating/comment.
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


@login_required
def submit_review(request: HttpRequest, slug: str) -> HttpResponse:
    """Create or update a farm review for the current customer."""
    farm = get_object_or_404(Farm, slug=slug)

    if not getattr(request.user, "is_customer", False):
        return HttpResponseForbidden("Only customer accounts can submit reviews.")

    if request.method != "POST":
        return redirect("farm_detail", slug=slug)

    existing = Review.objects.filter(farm=farm, customer=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.farm = farm
        review.customer = request.user
        # Basic server-side validation for rating bounds.
        if review.rating < 1:
            review.rating = 1
        if review.rating > 5:
            review.rating = 5
        review.save()
    return redirect("farm_detail", slug=slug)


@login_required
def address_list(request: HttpRequest) -> HttpResponse:
    """Customer address book for delivery planning."""
    if not getattr(request.user, "is_customer", False):
        return HttpResponseForbidden("Only customer accounts can manage delivery addresses.")

    addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-created_at")

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect("address_list")
    else:
        form = AddressForm()

    return render(
        request,
        "products/address_list.html",
        {
            "addresses": addresses,
            "form": form,
        },
    )


@login_required
def set_default_address(request: HttpRequest, pk: int) -> HttpResponse:
    """Mark a specific address as the default for the current customer."""
    if not getattr(request.user, "is_customer", False):
        return HttpResponseForbidden("Only customer accounts can manage delivery addresses.")

    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        address.is_default = True
        address.save()
    return redirect("address_list")


@login_required
def delivery_quote(request: HttpRequest, product_id: int) -> HttpResponse:
    """Show an estimated delivery quote for a given product and customer address."""
    if not getattr(request.user, "is_customer", False):
        return HttpResponseForbidden("Only customer accounts can request delivery quotes.")

    product = get_object_or_404(Product, pk=product_id, is_approved=True)
    farm = product.farm or getattr(product.farmer, "farm", None)
    if farm is None:
        return HttpResponseForbidden("This product is not linked to a farm for delivery planning.")

    # Select address: explicit id takes precedence, then default address.
    address_id = request.GET.get("address_id") or request.POST.get("address_id")
    address = None
    if address_id:
        address = get_object_or_404(Address, pk=address_id, user=request.user)
    else:
        address = Address.objects.filter(user=request.user, is_default=True).first()

    distance_km = None
    eta_minutes = None
    quoted_fee = None
    error = None

    if address is None:
        error = "Please add a delivery address before requesting a quote."
    else:
        try:
            distance_km, eta_minutes, quoted_fee = estimate_distance_and_fee(farm, address)
        except ValueError as exc:
            error = str(exc)

    return render(
        request,
        "products/delivery_quote.html",
        {
            "product": product,
            "farm": farm,
            "address": address,
            "distance_km": distance_km,
            "eta_minutes": eta_minutes,
            "quoted_fee": quoted_fee,
            "error": error,
        },
    )


@login_required
def delivery_create(request: HttpRequest, product_id: int) -> HttpResponse:
    """Persist a delivery request after the customer accepts the quote."""
    if request.method != "POST":
        return redirect("delivery_quote", product_id=product_id)

    if not getattr(request.user, "is_customer", False):
        return HttpResponseForbidden("Only customer accounts can request deliveries.")

    product = get_object_or_404(Product, pk=product_id, is_approved=True)
    farm = product.farm or getattr(product.farmer, "farm", None)
    if farm is None:
        return HttpResponseForbidden("This product is not linked to a farm for delivery planning.")

    address_id = request.POST.get("address_id")
    address = get_object_or_404(Address, pk=address_id, user=request.user)

    try:
        distance_km, eta_minutes, quoted_fee = estimate_distance_and_fee(farm, address)
    except ValueError as exc:
        return HttpResponse(str(exc), status=400)

    DeliveryRequest.objects.create(
        customer=request.user,
        farm=farm,
        pickup_address_text=farm.location or "Farm location",
        dropoff_address=address,
        distance_km=distance_km,
        eta_minutes=eta_minutes,
        quoted_fee=quoted_fee,
        status=DeliveryRequest.Status.QUOTED,
    )

    return redirect("delivery_list")


@login_required
def delivery_list(request: HttpRequest) -> HttpResponse:
    """Simple list of delivery requests for the current user."""
    qs = DeliveryRequest.objects.all()
    if getattr(request.user, "is_customer", False):
        qs = qs.filter(customer=request.user)
    elif getattr(request.user, "is_farmer", False):
        qs = qs.filter(farm__farmer=request.user)
    else:
        qs = qs.none()

    qs = qs.select_related("farm", "dropoff_address").order_by("-created_at")

    return render(
        request,
        "products/delivery_list.html",
        {
            "deliveries": qs,
        },
    )

