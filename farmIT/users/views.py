from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import FarmerUserCreationForm, FarmerProfileForm
from .models import FarmerProfile, CustomerProfile


class FarmerLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self) -> str:
        user = self.request.user
        # Route customers straight into the marketplace, farmers to their farm dashboard.
        if getattr(user, "is_customer", False):
            return reverse_lazy("product_list")
        return reverse_lazy("my_farm")


class FarmerLogoutView(LogoutView):
    next_page = "/"


def logout_redirect_login(request: HttpRequest) -> HttpResponse:
    """Allow GET logout and redirect to login page."""
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = FarmerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create role-specific profiles so we can safely expand later.
            if getattr(user, "is_farmer", False):
                FarmerProfile.objects.get_or_create(user=user)
                redirect_url = reverse_lazy("my_farm")
                role_message = "Set up your farm page to start listing products."
            else:
                CustomerProfile.objects.get_or_create(user=user)
                redirect_url = reverse_lazy("product_list")
                role_message = "Browse the marketplace and connect with farmers."

            login(request, user)
            messages.success(request, "Welcome to FarmIT!")
            messages.info(request, role_message)
            return redirect(redirect_url)
    else:
        form = FarmerUserCreationForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = FarmerProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated")
            return redirect("profile")
    else:
        form = FarmerProfileForm(instance=request.user)
    return render(request, "users/profile.html", {"form": form})


