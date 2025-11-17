from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..models import Product, Transaction


@staff_member_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    pending_products = Product.objects.filter(is_approved=False).count()
    reserved_products = Product.objects.filter(is_reserved=True).count()
    total_users = Product._meta.apps.get_model('users', 'FarmerUser').objects.count()
    total_interests = Transaction.objects.filter(status='interested').count()

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


