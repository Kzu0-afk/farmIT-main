from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import FarmerUserCreationForm, FarmerProfileForm


class FarmerLoginView(LoginView):
    template_name = 'registration/login.html'


class FarmerLogoutView(LogoutView):
    next_page = '/'

def logout_redirect_login(request: HttpRequest) -> HttpResponse:
    """Allow GET logout and redirect to login page."""
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = FarmerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to FarmIT!')
            return redirect('product_list')
    else:
        form = FarmerUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = FarmerProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated')
            return redirect('profile')
    else:
        form = FarmerProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


