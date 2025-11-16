from django.urls import path

from . import views


urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('marketplace/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    # Farm pages
    path('my-farm/', views.my_farm, name='my_farm'),
    path('farms/<slug:slug>/', views.farm_detail, name='farm_detail'),
    path('farms/<slug:slug>/review/', views.submit_review, name='submit_review'),
    # Transactions
    path('products/<int:pk>/interest/', views.create_interest, name='create_interest'),
    path('transactions/<int:tx_id>/reserve/', views.reserve_transaction, name='reserve_transaction'),
    # Delivery & addresses
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/<int:pk>/default/', views.set_default_address, name='set_default_address'),
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/quote/<int:product_id>/', views.delivery_quote, name='delivery_quote'),
    path('deliveries/create/<int:product_id>/', views.delivery_create, name='delivery_create'),
    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

