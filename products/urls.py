# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('new-arrivals/', views.NewArrivalsView.as_view(), name='new_arrivals'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('api/quick-view/<slug:slug>/', views.quick_view, name='quick_view'),
    path('api/products/', views.products_api, name='products_api'),
    path('api/featured/', views.featured_products_api, name='featured_products_api'),
    path('api/wishlist/', views.wishlist_products_api, name='wishlist_products_api'),
    path('api/product-filter/', views.product_filter_ajax, name='product_filter_ajax'),
    path('review/<slug:slug>/submit/', views.submit_review, name='submit_review'),
    path('contact/<slug:slug>/submit/', views.contact_submit, name='contact_submit'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('profile/', views.profile_view, name='profile'),
    path('orders/', views.orders_view, name='orders'),
    path('provider-logs/', views.provider_logs_view, name='provider_logs'),
    path('debug/', views.debug_products, name='debug_products'),
]