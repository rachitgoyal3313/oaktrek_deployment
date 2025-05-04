from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.auth_view, name='auth'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('addresses/', views.address_list_view, name='address_list'),
    path('add_address/', views.add_address, name='add_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('add_phone/', views.add_phone, name='add_phone'),
    path('change_password/', views.change_password, name='change_password'),
    path('admin_signin/', views.admin_signin, name='admin_signin'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),
    path('admin/products/', views.admin_products_view, name='adminProducts'),
    path('admin/products/add/', views.add_product, name='add_product'),
    path('admin/products/view/<int:product_id>/', views.view_product, name='view_product'),
    path('admin/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admin/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin/products/bulk_delete/', views.bulk_delete_products, name='bulk_delete_products'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]