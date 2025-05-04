from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('products/<slug:collection_name>/<slug:product_slug>/', views.product_page_view, name='product_page'),
    path('products/category/<str:gender>/<str:collection_name>', views.products_cat_view, name="products-cat"),  
    path('<str:collection_name>/<slug:product_slug>/add-review/', views.add_review, name='add_review'),
    path('products/<str:collection_name>/', views.products_view, name='products'),
    path('stores/', views.stores, name='stores'),
    path('coming_soon/', views.coming_soon, name='coming_soon'),
    path('moonshot/', views.moonshot, name='moonshot'),
    path('adidasxoaktrek/', views.adidasxoaktrek, name='adidasxoaktrek'),
    path('bcorp/', views.bcorp, name='bcorp'),
    path('join/', views.join, name='join'),
    path('mothernature/', views.mothernature, name='mothernature'),
    path('carbonFootprint/', views.carbonFootprint, name='carbonoffsets'),
    path('oaktrek_help/', views.oaktrek_help, name='oaktrek_help'),
    path('returns/', views.returns, name='returns'),
    path('faq/', views.faq, name='faq'),
    path('aboutUs/', views.aboutUs, name='about_us'),
    path('our_story/', views.our_story, name='our_story'),
    path('our_materials/', views.our_materials, name='our_materials'),
    path('sustainability/', views.sustainability, name='sustainability'),
    path('regenerative/', views.regenerative, name='regenerative'),
    path('renewable/', views.renewable, name='renewable'),
    path('terms/', views.terms, name='terms'),
    path('responsibleEnergy/', views.responsibleEnergy, name='responsibleEnergy'),
    path('products/mens-apparel/', views.products_view, name='mens_apparel'),
    path('products/womens-apparel/', views.products_view, name='womens_apparel'),
    path('products/socks/', views.products_view, name='socks'),
    path('cart/', views.cart_view, name='cart'),
    path('page_not_found/', views.error_page, name='page_not_found'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout,  name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('inventory/dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/low-stock/', views.low_stock_alerts, name='low_stock_alerts'),
    path('inventory/update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    path('inventory/product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    # API Endpoints
    path('api/inventory/stock-history/<int:product_id>/', views.stock_history_api, name='stock_history_api'),
    path('api/inventory/category-comparison/', views.category_comparison_api, name='category_comparison_api'),
    path('api/inventory/stock-sales/<int:product_id>/', views.stock_sales_api, name='stock_sales_api'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)