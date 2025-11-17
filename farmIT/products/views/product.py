from django.contrib.admin.views.decorators import staff_member_required  # noqa: F401  # kept for parity if needed elsewhere
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Prefetch, Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ProductForm
from ..models import Farm, Product, Transaction


def product_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    page_number = request.GET.get('page', 1)

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

    paginator = Paginator(products, 12)
    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    highlight_farms = (
        Farm.objects.filter(products__is_approved=True)
        .exclude(slug="")
        .annotate(active_products=Count("products", distinct=True))
        .order_by("-active_products", "name")
        .prefetch_related(
            Prefetch(
                "products",
                queryset=Product.objects.filter(is_approved=True).order_by("-created_at"),
                to_attr="top_products",
            )
        )[:8]
    )

    return render(
        request,
        'products/product_list.html',
        {
            'products': products_page,
            'query': query,
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            'highlight_farms': highlight_farms,
        },
    )


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
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
    if not getattr(request.user, "is_farmer", False):
        return HttpResponseForbidden("Only farmer accounts can create product listings.")

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            farm = getattr(request.user, "farm", None)
            if farm:
                product.farm = farm
            product.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})


@login_required
def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    if not getattr(request.user, "is_farmer", False):
        return HttpResponseForbidden("Only farmer accounts can manage product listings.")

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
    if not getattr(request.user, "is_farmer", False):
        return HttpResponseForbidden("Only farmer accounts can manage product listings.")

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


