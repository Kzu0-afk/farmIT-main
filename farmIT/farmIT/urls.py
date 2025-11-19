"""
URL configuration for farmIT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

def empty_favicon(_request):
    """Return 204 to avoid noisy /favicon.ico 404s when no icon is provided."""
    return HttpResponse(status=204, content_type='image/x-icon')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('chat/', include('chat.urls')),
    path('', include('products.urls')),
    # Handle favicon explicitly so browsers don't log 404s
    path('favicon.ico', empty_favicon),
]
