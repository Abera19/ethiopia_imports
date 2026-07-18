from django import template
from django.utils import timezone
from decimal import Decimal

register = template.Library()


@register.filter
def currency(value):
    """Format number as ETB currency"""
    try:
        return f"ETB {Decimal(value):,.2f}"
    except (ValueError, TypeError):
        return "ETB 0.00"


@register.filter
def in_stock(product):
    """Check if product is in stock"""
    return product.stock_quantity > 0


@register.filter
def stock_status(product):
    """Get human-readable stock status"""
    if product.stock_quantity > 10:
        return 'In Stock'
    elif product.stock_quantity > 0:
        return f'Only {product.stock_quantity} left!'
    else:
        return 'Out of Stock'


@register.filter
def stars_rating(value):
    """Generate star rating HTML"""
    try:
        rating = float(value)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)

        stars = '★' * full_stars
        if half_star:
            stars += '½'
        stars += '☆' * empty_stars
        return stars
    except (ValueError, TypeError):
        return '☆☆☆☆☆'


# ===== NEW: Multiply Filter =====
@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value


# ===== NEW: Subtract Filter =====
@register.filter
def subtract(value, arg):
    """Subtract the argument from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value


# ===== NEW: Add Filter (Override) =====
@register.filter
def add(value, arg):
    """Add the argument to the value"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value