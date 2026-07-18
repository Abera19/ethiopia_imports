from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'products'

urlpatterns = [
    # Main product listing and detail
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # AJAX endpoints
    path('api/featured/', views.featured_products_api, name='featured_api'),
    path('api/filter/', views.product_filter_ajax, name='product_filter'),
    path('api/quick-view/<slug:slug>/', views.quick_view, name='quick_view'),
    path('api/contact/<slug:slug>/', views.contact_submit, name='contact_submit'),
    path('api/products/', views.products_api, name='products_api'),
    path('api/review/<slug:slug>/', views.submit_review, name='submit_review'),
    path('api/wishlist-products/', views.wishlist_products_api, name='wishlist_products_api'),
    # Admin-only provider logs
    path('provider-logs/', views.provider_logs_view, name='provider_logs'),

    # User pages (add these)
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('profile/', views.profile_view, name='profile'),
    path('orders/', views.orders_view, name='orders'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)