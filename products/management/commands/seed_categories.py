# products/management/commands/seed_categories.py
from django.core.management.base import BaseCommand
from products.models import Category
from django.core.files import File
import requests
from io import BytesIO

class Command(BaseCommand):
    help = 'Seed categories with images'

    def handle(self, *args, **options):
        # Category image URLs (replace with your actual image URLs)
        category_images = {
            'electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400',
            'clothing': 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400',
            'books': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400',
            'furniture': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400',
            'home-appliances': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400',
            '3d-product': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400',
            'new-product': 'https://images.unsplash.com/photo-1503602642458-232111445657?w=400',
        }

        for slug, image_url in category_images.items():
            try:
                category = Category.objects.get(slug=slug)
                response = requests.get(image_url)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    category.image.save(f'{slug}.jpg', File(img_data), save=True)
                    self.stdout.write(f'✅ Added image to {category.name}')
            except Category.DoesNotExist:
                self.stdout.write(f'⚠️ Category {slug} not found')
            except Exception as e:
                self.stdout.write(f'❌ Error: {e}')