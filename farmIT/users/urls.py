from django.urls import path

from .views import FarmerLoginView, FarmerLogoutView, profile, register


urlpatterns = [
    path('login/', FarmerLoginView.as_view(), name='login'),
    path('logout/', FarmerLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
]


