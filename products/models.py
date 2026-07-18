from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='tag')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=200, default='Imported from China')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if self.stock_quantity == 0:
            if self.status == 'active':
                self.status = 'out_of_stock'
        else:
            if self.status == 'out_of_stock':
                self.status = 'active'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


# ===== ProductImage - Defined AFTER Product =====
class ProductImage(models.Model):
    """Multiple images for a product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False, help_text='Set as main product image')
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return f"{self.product.title} - Image {self.order}"


class ProductProvider(models.Model):
    """Admin-only model for tracking product suppliers and costs"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='provider_info')
    supplier_name = models.CharField(max_length=200)
    supplier_contact = models.CharField(max_length=200, blank=True)
    supplier_country = models.CharField(max_length=100, default='China')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    shipping_status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('shipped', 'Shipped'),
            ('transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('customs', 'Customs Clearance'),
        ],
        default='pending'
    )
    shipping_tracking = models.CharField(max_length=100, blank=True)
    expected_arrival = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Product Providers'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.product.title} - {self.supplier_name}"


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    session_id = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['product', 'session_id']),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.viewed_at}"


class ContactMessage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='messages')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.product.title}"


class ProductReview(models.Model):
    """Customer reviews for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
        ]

    def __str__(self):
        return f"{self.name} - {self.product.title} - {self.rating}★"


# ===== SiteSettings - Editable site content =====
class SiteSettings(models.Model):
    """Editable site settings for admin"""
    # Logo & Branding
    eth_text = models.CharField(max_length=10, default='ETH', help_text='Main logo text (e.g., ETH)')
    brand_suffix = models.CharField(max_length=50, default=' Imports', help_text='Text after ETH (e.g., " Imports")')
    eth_e_color = models.CharField(max_length=20, default='#0F8B4C', help_text='Color for "E" in ETH')
    eth_t_color = models.CharField(max_length=20, default='#F6B100', help_text='Color for "T" in ETH')
    eth_h_color = models.CharField(max_length=20, default='#EF4444', help_text='Color for "H" in ETH')

    # Header
    site_name = models.CharField(max_length=100, default='ETH Imports')
    header_tagline = models.CharField(max_length=200, blank=True, default='Premium Ethiopian Imported Products')

    # Hero Section
    hero_badge = models.CharField(max_length=100, default='Summer Sale')
    hero_title = models.CharField(max_length=200, default='Discover Premium Ethiopian Imports')
    hero_subtitle = models.TextField(
        default='Curated collection of high-quality products from around the world, delivered to your doorstep.')
    hero_button_text = models.CharField(max_length=50, default='Shop Now')
    hero_button_url = models.CharField(max_length=200, default='#products')
    hero_secondary_button_text = models.CharField(max_length=50, default='Watch Story')
    hero_secondary_button_url = models.CharField(max_length=200, default='#')

    # Category Section
    categories_title = models.CharField(max_length=100, default='Shop by Category')
    categories_view_all = models.CharField(max_length=50, default='View All')

    # Footer
    footer_brand = models.CharField(max_length=100, default='ETH Imports')
    footer_tagline = models.CharField(max_length=200,
                                      default='Premium products for discerning customers. Curated with care, delivered with excellence.')
    footer_copyright = models.CharField(max_length=200, default='All rights reserved.')

    # Contact
    whatsapp_number = models.CharField(max_length=20, default='+251900000000')
    telegram_username = models.CharField(max_length=50, default='your_username')

    # Social Media
    facebook_url = models.URLField(blank=True, default='#')
    instagram_url = models.URLField(blank=True, default='#')
    twitter_url = models.URLField(blank=True, default='#')
    youtube_url = models.URLField(blank=True, default='#')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'