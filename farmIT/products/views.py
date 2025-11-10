from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product, Transaction


def landing_page(request: HttpRequest) -> HttpResponse:
    """Landing page with hero section and info about FarmIT"""
    return render(request, 'products/landing_page.html')


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

    return render(request, 'products/product_list.html', {
        'products': products,
        'query': query,
        'location': location,
        'min_price': min_price,
        'max_price': max_price,
    })


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
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})


@login_required
def product_update(request: HttpRequest, pk: int) -> HttpResponse:
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
