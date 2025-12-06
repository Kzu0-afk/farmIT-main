from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def landing_page(request: HttpRequest) -> HttpResponse:
    """Landing page with hero section and info about FarmIT.
    
    Accessible to all users (authenticated or not). 
    Customers are redirected to marketplace on login, but can still view 
    the landing page by clicking the FarmIT logo.
    """
    return render(request, "products/landing_page.html")


