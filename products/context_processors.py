from django.conf import settings
from .models import Category, Product, SiteSettings


def site_context(request):
    """Context processor for common site data"""
    return {
        'categories': Category.objects.all(),
        'featured_products': Product.objects.filter(status='active', featured=True)[:6],
        'whatsapp_number': settings.WHATSAPP_NUMBER,
        'telegram_username': settings.TELEGRAM_USERNAME,
        'site_name': 'Ethiopia Imports',
        'current_path': request.path,
    }


def site_context(request):
    """Context processor for common site data"""
    # Get site settings
    try:
        site_settings = SiteSettings.objects.first()
    except:
        site_settings = None

    context = {
        'categories': Category.objects.all(),
        'featured_products': Product.objects.filter(status='active', featured=True)[:6],
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