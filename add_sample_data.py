# add_sample_data.py
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethiopia_imports.settings')

import django

django.setup()

from products.models import Category, Product
from django.utils.text import slugify
from django.db import IntegrityError


def add_sample_data():
    print("Adding sample data...")

    # Create categories with proper handling
    categories_data = [
        {'name': 'Electronics', 'slug': 'electronics'},
        {'name': 'Furniture', 'slug': 'furniture'},
        {'name': 'Clothing', 'slug': 'clothing'},
        {'name': 'Home Appliances', 'slug': 'home-appliances'},
        {'name': 'Books', 'slug': 'books'},
    ]

    categories = {}
    for cat_data in categories_data:
        try:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            categories[cat_data['slug']] = category
            if created:
                print(f"✓ Created category: {category.name}")
            else:
                print(f"• Category already exists: {category.name}")
        except IntegrityError:
            # If slug exists, try to get it
            category = Category.objects.get(slug=cat_data['slug'])
            categories[cat_data['slug']] = category
            print(f"• Found existing category: {category.name}")

    # Create products
    products_data = [
        {
            'title': 'Smartphone X Pro',
            'description': 'High-end smartphone with 6.7" display, 128GB storage, and 5G connectivity.',
            'price': 45000.00,
            'category_slug': 'electronics',
            'stock_quantity': 15,
            'source': 'Imported from China',
            'featured': True,
        },
        {
            'title': 'Laptop Ultra Slim',
            'description': 'Lightweight laptop with 16GB RAM, 512GB SSD, and 14" 4K display.',
            'price': 85000.00,
            'category_slug': 'electronics',
            'stock_quantity': 8,
            'source': 'Imported from Japan',
            'featured': True,
        },
        {
            'title': 'Modern Sofa Set',
            'description': 'Comfortable 3-seater sofa with premium fabric and wooden frame.',
            'price': 32000.00,
            'category_slug': 'furniture',
            'stock_quantity': 5,
            'source': 'Imported from Turkey',
            'featured': False,
        },
        {
            'title': 'Dining Table Set',
            'description': 'Elegant 6-seater dining table with matching chairs, solid wood construction.',
            'price': 28000.00,
            'category_slug': 'furniture',
            'stock_quantity': 3,
            'source': 'Imported from Italy',
            'featured': False,
        },
        {
            'title': 'Ethiopian Traditional Dress',
            'description': 'Beautiful hand-woven cotton dress with traditional Ethiopian patterns.',
            'price': 3500.00,
            'category_slug': 'clothing',
            'stock_quantity': 25,
            'source': 'Made in Ethiopia',
            'featured': True,
        },
        {
            'title': 'Wireless Headphones',
            'description': 'Noise-cancelling headphones with 30-hour battery life and premium sound quality.',
            'price': 8500.00,
            'category_slug': 'electronics',
            'stock_quantity': 20,
            'source': 'Imported from South Korea',
            'featured': False,
        },
        {
            'title': 'Air Fryer Pro',
            'description': 'Digital air fryer with 5.8L capacity, 8 cooking presets, and oil-free frying.',
            'price': 15000.00,
            'category_slug': 'home-appliances',
            'stock_quantity': 10,
            'source': 'Imported from Germany',
            'featured': True,
        },
        {
            'title': 'Ethiopian Cookbook',
            'description': 'Traditional Ethiopian recipes and cooking techniques from expert chefs.',
            'price': 1200.00,
            'category_slug': 'books',
            'stock_quantity': 30,
            'source': 'Printed in Ethiopia',
            'featured': False,
        },
    ]

    products_created = 0
    for data in products_data:
        try:
            # Get the category
            category = categories.get(data['category_slug'])
            if not category:
                print(f"✗ Category not found for: {data['title']}")
                continue

            # Create or get product
            product, created = Product.objects.get_or_create(
                title=data['title'],
                defaults={
                    'slug': slugify(data['title']),
                    'description': data['description'],
                    'price': data['price'],
                    'category': category,
                    'stock_quantity': data['stock_quantity'],
                    'source': data['source'],
                    'featured': data['featured'],
                    'status': 'active'
                }
            )
            if created:
                products_created += 1
                print(f"✓ Created product: {product.title} ({product.price} ETB)")
            else:
                print(f"• Product already exists: {product.title}")
        except Exception as e:
            print(f"✗ Error creating product {data['title']}: {e}")

    # Summary
    print(f"\n{'=' * 50}")
    print(f"✅ Sample data added successfully!")
    print(f"📊 Total Categories: {Category.objects.count()}")
    print(f"📦 Total Products: {Product.objects.count()}")
    print(f"🆕 New Products Created: {products_created}")
    print(f"{'=' * 50}")

    # Show all products
    print("\n📋 Product List:")
    for product in Product.objects.all():
        print(f"  - {product.title}: {product.price} ETB ({product.source})")


if __name__ == '__main__':
    add_sample_data()