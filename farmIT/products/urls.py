from django.urls import path

from . import views


urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    # Transactions
    path('products/<int:pk>/interest/', views.create_interest, name='create_interest'),
    path('transactions/<int:tx_id>/reserve/', views.reserve_transaction, name='reserve_transaction'),
    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]


