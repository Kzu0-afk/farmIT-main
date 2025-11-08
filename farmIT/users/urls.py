from django.urls import path

from .views import FarmerLoginView, FarmerLogoutView, profile, register, logout_redirect_login


urlpatterns = [
    path('login/', FarmerLoginView.as_view(), name='login'),
    # Use GET-friendly logout that redirects to login
    path('logout/', logout_redirect_login, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
]


