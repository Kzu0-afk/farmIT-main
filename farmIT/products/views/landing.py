from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def landing_page(request: HttpRequest) -> HttpResponse:
    """Landing page with hero section and info about FarmIT.

    For logged-in customers, we treat the marketplace as their primary home.
    """
    user = request.user
    if getattr(user, "is_authenticated", False) and getattr(user, "is_customer", False):
        return redirect("product_list")
    return render(request, "products/landing_page.html")


