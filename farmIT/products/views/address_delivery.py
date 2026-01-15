from decimal import Decimal  # noqa: F401  # retained for potential future fee overrides

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from farmIT.throttling import check_throttle

from ..forms import AddressForm
from ..models import Address, DeliveryRequest, Product, estimate_distance_and_fee


@login_required
def address_list(request: HttpRequest) -> HttpResponse:
    """Customer address book for delivery planning."""
    if not getattr(request.user, "is_customer", False):
        return HttpResponse("Only customer accounts can manage delivery addresses.", status=403)

    addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-created_at")

    if request.method == "POST":
        throttle = check_throttle(f"addr:create:{request.user.id}", limit=20, window_seconds=60)
        if not throttle.allowed:
            return HttpResponse("Too many requests, please slow down.", status=429)

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
        return HttpResponse("Only customer accounts can manage delivery addresses.", status=403)

    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        throttle = check_throttle(f"addr:set_default:{request.user.id}", limit=60, window_seconds=60)
        if not throttle.allowed:
            return HttpResponse("Too many requests, please slow down.", status=429)

        # Ensure a single default address per customer.
        Address.objects.filter(user=request.user, is_default=True).exclude(pk=address.pk).update(is_default=False)
        address.is_default = True
        address.save()
    return redirect("address_list")


@login_required
def delivery_quote(request: HttpRequest, product_id: int) -> HttpResponse:
    """Show an estimated delivery quote for a given product and customer address."""
    if not getattr(request.user, "is_customer", False):
        return HttpResponse("Only customer accounts can request delivery quotes.", status=403)

    throttle = check_throttle(f"delivery:quote:{request.user.id}", limit=30, window_seconds=60)
    if not throttle.allowed:
        return HttpResponse("Too many requests, please slow down.", status=429)

    product = get_object_or_404(Product, pk=product_id, is_approved=True)
    farm = product.farm or getattr(product.farmer, "farm", None)
    if farm is None:
        return HttpResponse("This product is not linked to a farm for delivery planning.", status=403)

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
    elif farm.latitude is None or farm.longitude is None:
        error = (
            "This farm has no map coordinates yet. Please ask the farmer to update their "
            "location so delivery quotes can be calculated."
        )
    elif address.latitude is None or address.longitude is None:
        error = (
            "Your selected address does not have map coordinates yet. Edit the address and "
            "add its latitude and longitude in decimal degrees."
        )
    else:
        try:
            distance_km, eta_minutes, quoted_fee = estimate_distance_and_fee(farm, address)
        except ValueError as exc:
            # Fall back to a generic message; avoid leaking internal details.
            error = "We could not calculate a delivery quote for this route. Please double-check the coordinates."

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
        return HttpResponse("Only customer accounts can request deliveries.", status=403)

    throttle = check_throttle(f"delivery:create:{request.user.id}", limit=10, window_seconds=60)
    if not throttle.allowed:
        return HttpResponse("Too many requests, please slow down.", status=429)

    product = get_object_or_404(Product, pk=product_id, is_approved=True)
    farm = product.farm or getattr(product.farmer, "farm", None)
    if farm is None:
        return HttpResponse("This product is not linked to a farm for delivery planning.", status=403)

    address_id = request.POST.get("address_id")
    address = get_object_or_404(Address, pk=address_id, user=request.user)

    if farm.latitude is None or farm.longitude is None:
        return HttpResponse(
            "This farm has no map coordinates yet. Please contact the farmer to update their location.",
            status=400,
        )
    if address.latitude is None or address.longitude is None:
        return HttpResponse(
            "This address does not have map coordinates yet. Edit the address and add latitude and longitude.",
            status=400,
        )

    try:
        distance_km, eta_minutes, quoted_fee = estimate_distance_and_fee(farm, address)
    except ValueError:
        return HttpResponse(
            "We could not calculate a delivery quote for this route. Please double-check the coordinates.",
            status=400,
        )

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


