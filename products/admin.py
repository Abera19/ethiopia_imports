from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from .models import Category, Product, ProductImage, ProductProvider, ProductView, ContactMessage, ProductReview, \
    SiteSettings


class InStockFilter(SimpleListFilter):
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock_quantity__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(stock_quantity=0)
        return queryset


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'is_primary', 'order')
    max_num = 10


class ProductProviderInline(admin.StackedInline):
    model = ProductProvider
    can_delete = False
    verbose_name_plural = 'Provider Information'
    fieldsets = (
        ('Supplier Information', {
            'fields': ('supplier_name', 'supplier_contact', 'supplier_country', 'cost_price')
        }),
        ('Shipping Details', {
            'fields': ('shipping_status', 'shipping_tracking', 'expected_arrival')
        }),
        ('Additional Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'stock_quantity', 'status', 'category', 'featured', 'created_at']
    list_filter = ['status', 'category', 'featured', InStockFilter]
    search_fields = ['title', 'description', 'source']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['price', 'stock_quantity', 'status', 'featured']
    actions = ['make_active', 'make_inactive', 'make_featured']
    inlines = [ProductProviderInline, ProductImageInline]  # Added ProductImageInline

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category', 'image')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'source')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'featured')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('provider-logs/', self.admin_site.admin_view(self.provider_logs_view), name='provider_logs'),
        ]
        return custom_urls + urls

    def provider_logs_view(self, request):
        context = {
            'title': 'Product Provider Logs',
            'provider_logs': ProductProvider.objects.select_related('product').all(),
            'total_providers': ProductProvider.objects.count(),
            'total_products': Product.objects.count(),
        }
        return render(request, 'admin/products/provider_logs.html', context)

    def make_active(self, request, queryset):
        queryset.update(status='active')

    make_active.short_description = "Mark selected products as Active"

    def make_inactive(self, request, queryset):
        queryset.update(status='inactive')

    make_inactive.short_description = "Mark selected products as Inactive"

    def make_featured(self, request, queryset):
        queryset.update(featured=True)

    make_featured.short_description = "Mark selected products as Featured"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'product_count']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['parent']

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Number of Products'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order']
    list_filter = ['is_primary']
    search_fields = ['product__title', 'alt_text']
    list_editable = ['is_primary', 'order']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">'
        return 'No Image'

    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


@admin.register(ProductProvider)
class ProductProviderAdmin(admin.ModelAdmin):
    list_display = ['product', 'supplier_name', 'supplier_country', 'cost_price', 'shipping_status', 'updated_at']
    list_filter = ['shipping_status', 'supplier_country']
    search_fields = ['product__title', 'supplier_name', 'shipping_tracking']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Product Information', {
            'fields': ('product',)
        }),
        ('Supplier Details', {
            'fields': ('supplier_name', 'supplier_contact', 'supplier_country', 'cost_price')
        }),
        ('Shipping Information', {
            'fields': ('shipping_status', 'shipping_tracking', 'expected_arrival')
        }),
        ('Notes', {
            'fields': ('notes',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'email', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    mark_as_unread.short_description = "Mark selected messages as unread"


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product', 'session_id', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['product__title', 'session_id']
    readonly_fields = ['viewed_at']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['name', 'email', 'comment', 'product__title']
    list_editable = ['is_approved']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    approve_reviews.short_description = "Approve selected reviews"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Logo & Branding', {
            'fields': ('eth_text', 'brand_suffix', 'eth_e_color', 'eth_t_color', 'eth_h_color')
        }),
        ('Header Settings', {
            'fields': ('site_name', 'header_tagline')
        }),
        ('Hero Section', {
            'fields': ('hero_badge', 'hero_title', 'hero_subtitle',
                       'hero_button_text', 'hero_button_url',
                       'hero_secondary_button_text', 'hero_secondary_button_url')
        }),
        ('Categories Section', {
            'fields': ('categories_title', 'categories_view_all')
        }),
        ('Footer Settings', {
            'fields': ('footer_brand', 'footer_tagline', 'footer_copyright')
        }),
        ('Contact Info', {
            'fields': ('whatsapp_number', 'telegram_username')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'youtube_url')
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)