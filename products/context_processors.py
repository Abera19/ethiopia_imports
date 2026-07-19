# products/context_processors.py
from django.conf import settings
from .models import Category, Product, SiteSettings
from django.utils import timezone
from datetime import timedelta


def new_arrivals_count(request):
    """Get count of new arrivals from the last 30 days"""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    count = Product.objects.filter(
        created_at__gte=thirty_days_ago,
        status='active'
    ).count()
    return {
        'new_arrivals_count': count
    }


def site_context(request):
    """Context processor for common site data"""
    # Get site settings
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None

    context = {
        'categories': Category.objects.all(),
        # REMOVED: 'featured_products': Product.objects.filter(status='active', featured=True)[:6],
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '+251900000000'),
        'telegram_username': getattr(settings, 'TELEGRAM_USERNAME', 'your_username'),
        'site_name': 'ETH Imports',
        'current_path': request.path,
    }

    # Add site settings if available
    if site_settings:
        context.update({
            'site_settings': site_settings,
            'site_name': site_settings.site_name,
        })

    return context