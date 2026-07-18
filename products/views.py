from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, Min, Max
from django.contrib import messages
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import json
import logging
from .models import Product, Category, ProductView, ContactMessage, ProductReview
from .filters import ProductFilter
from .forms import ContactForm, ReviewForm

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ProductListView(ListView):
    model = Product
    template_name = 'product_list_premium.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(status='active').select_related('category')

        # Debug - print count
        print(f"DEBUG: Total active products before filters: {queryset.count()}")

        # Search functionality
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(source__icontains=search_query)
            )
            print(f"DEBUG: After search filter: {queryset.count()}")

        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                queryset = queryset.filter(category=category)
                print(f"DEBUG: After category filter ({category.name}): {queryset.count()}")
            except Category.DoesNotExist:
                print(f"DEBUG: Category not found: {category_slug}")
                pass

        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # In stock filter
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)

        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        allowed_sorts = ['price', '-price', 'created_at', '-created_at', 'title', '-title', 'rating', 'popular']
        if sort_by in allowed_sorts:
            if sort_by in ['rating', 'popular']:
                sort_by = '-created_at'  # Fallback for rating/popular
            queryset = queryset.order_by(sort_by)

        print(f"DEBUG: Final queryset count: {queryset.count()}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all categories for sidebar
        context['categories'] = Category.objects.all().prefetch_related('subcategories')

        # Get price range for filter
        price_agg = Product.objects.filter(status='active').aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        context['min_price'] = int(price_agg['min_price'] or 0)
        context['max_price'] = int(price_agg['max_price'] or 100000)

        # Current filter values
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'q': self.request.GET.get('q', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
            'in_stock': self.request.GET.get('in_stock', ''),
        }

        # Pass products as JSON for JavaScript
        product_list = []
        for product in context['products']:
            product_list.append({
                'id': product.id,
                'title': product.title,
                'slug': product.slug,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
                'source': product.source,
                'stock_quantity': product.stock_quantity,
                'in_stock': product.stock_quantity > 0,
                'featured': product.featured,
            })
        context['products_json'] = json.dumps(product_list)

        return context


# ===== SINGLE ProductDetailView - Merged with all functionality =====
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail_premium.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(status='active').select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Track product view
        self.track_product_view(product)

        # Get related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id)[:4]

        # Get product view count
        context['view_count'] = ProductView.objects.filter(product=product).count()

        # Get approved reviews
        context['reviews'] = ProductReview.objects.filter(
            product=product,
            is_approved=True
        )[:10]

        # Get average rating
        avg_rating = ProductReview.objects.filter(
            product=product,
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg']
        context['avg_rating'] = avg_rating or 0
        context['review_count'] = ProductReview.objects.filter(
            product=product,
            is_approved=True
        ).count()

        # Review form
        context['review_form'] = ReviewForm()

        # WhatsApp and Telegram URLs
        whatsapp_message = f"Hello, I want to order {product.title} for {product.price} ETB."
        context['whatsapp_url'] = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={whatsapp_message}"
        context['telegram_url'] = f"https://t.me/{settings.TELEGRAM_USERNAME}?text={whatsapp_message}"

        # Contact form
        context['contact_form'] = ContactForm()

        return context

    def track_product_view(self, product):
        """Track product views with session-based counting"""
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key

        try:
            ProductView.objects.create(
                product=product,
                session_id=session_key,
                ip_address=get_client_ip(self.request)
            )
        except Exception:
            # Silently fail if tracking fails
            pass


def submit_review(request, slug):
    """Submit a product review"""
    product = get_object_or_404(Product, slug=slug, status='active')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.user = request.user
                review.name = request.user.get_full_name() or request.user.username
                review.email = request.user.email
            review.save()
            return JsonResponse({
                'success': True,
                'message': 'Your review has been submitted and will be reviewed shortly.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def provider_logs_view(request):
    """Admin-only view for provider logs"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('products:product_list')

    products = Product.objects.select_related('provider_info').all()
    context = {
        'products': products,
        'total_cost': sum(p.provider_info.cost_price for p in products if hasattr(p, 'provider_info')),
        'total_products': products.count(),
    }
    return render(request, 'admin/products/provider_logs.html', context)


def contact_submit(request, slug):
    """Handle contact form submissions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    product = get_object_or_404(Product, slug=slug, status='active')
    form = ContactForm(request.POST)

    if form.is_valid():
        ContactMessage.objects.create(
            product=product,
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data.get('phone', ''),
            message=form.cleaned_data['message'],
        )
        return JsonResponse({
            'success': True,
            'message': 'Your message has been sent successfully!'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


def quick_view(request, slug):
    """AJAX endpoint for quick product preview"""
    product = get_object_or_404(Product, slug=slug, status='active')

    data = {
        'id': product.id,
        'title': product.title,
        'description': product.description[:200],
        'price': str(product.price),
        'image_url': product.image.url if product.image else None,
        'stock': product.stock_quantity,
        'in_stock': product.is_in_stock,
        'category': product.category.name if product.category else None,
        'source': product.source,
    }

    return JsonResponse(data)


def product_filter_ajax(request):
    """AJAX endpoint for filtered product results"""
    products = Product.objects.filter(status='active')
    filter_obj = ProductFilter(request.GET, queryset=products)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(filter_obj.qs, 12)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Render product grid items
    html = render(request, 'products/_product_grid.html', {
        'products': products_page,
        'page_obj': products_page,
    }).content.decode('utf-8')

    return JsonResponse({
        'html': html,
        'has_next': products_page.has_next(),
        'page': products_page.number,
        'total_pages': paginator.num_pages,
    })


def featured_products_api(request):
    """API endpoint for featured products"""
    products = Product.objects.filter(status='active', featured=True)[:8]

    data = []
    for product in products:
        data.append({
            'id': product.id,
            'title': product.title,
            'price': str(product.price),
            'image_url': product.image.url if product.image else None,
            'slug': product.slug,
        })

    return JsonResponse({'products': data})


def products_api(request):
    """API endpoint for products with filters"""
    products = Product.objects.filter(status='active')

    # Apply filters
    search = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', '-created_at')

    if search:
        products = products.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(source__icontains=search)
        )

    if category:
        products = products.filter(category__slug=category)

    if min_price:
        products = products.filter(price__gte=float(min_price))

    if max_price:
        products = products.filter(price__lte=float(max_price))

    # Sorting
    sort_mapping = {
        'price': 'price',
        '-price': '-price',
        'title': 'title',
        '-title': '-title',
        'rating': '-created_at',
        'popular': '-created_at',
    }
    sort_field = sort_mapping.get(sort, '-created_at')
    products = products.order_by(sort_field)

    # Serialize
    product_list = []
    for product in products:
        product_list.append({
            'id': product.id,
            'title': product.title,
            'slug': product.slug,
            'description': product.description[:200],
            'price': float(product.price),
            'image': product.image.url if product.image else None,
            'source': product.source,
            'stock_quantity': product.stock_quantity,
            'category_slug': product.category.slug if product.category else None,
            'category_name': product.category.name if product.category else None,
            'created_at': product.created_at.isoformat(),
            'featured': product.featured,
            'in_stock': product.stock_quantity > 0,
        })

    return JsonResponse(product_list, safe=False)


def wishlist_products_api(request):
    """API endpoint for wishlist products by IDs"""
    import json
    product_ids = request.GET.get('ids', '')

    if not product_ids:
        return JsonResponse({'products': []})

    try:
        ids = [int(id) for id in product_ids.split(',') if id.isdigit()]
        products = Product.objects.filter(id__in=ids, status='active')

        data = []
        for product in products:
            data.append({
                'id': product.id,
                'title': product.title,
                'slug': product.slug,
                'description': product.description[:200],
                'price': str(product.price),
                'image_url': product.image.url if product.image else None,
                'source': product.source,
                'in_stock': product.is_in_stock,
            })

        return JsonResponse({'products': data})
    except:
        return JsonResponse({'products': []})
@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    # Since wishlist is stored in localStorage, we need to pass products
    # that the user has in their wishlist
    # For now, we'll display a message
    context = {
        'page_title': 'My Wishlist',
        'message': 'Your wishlist items will appear here. Add products to your wishlist by clicking the heart icon.',
    }
    return render(request, 'products/wishlist.html', context)

@login_required
def profile_view(request):
    """Display user's profile"""
    context = {
        'page_title': 'My Profile',
        'user': request.user,
    }
    return render(request, 'products/profile.html', context)

@login_required
def orders_view(request):
    """Display user's orders"""
    # For now, show empty orders
    context = {
        'page_title': 'My Orders',
        'message': 'Your orders will appear here once you make a purchase.',
    }
    return render(request, 'products/orders.html', context)

def debug_products(request):
    """Debug view to check products"""
    all_products = Product.objects.all()
    active_products = Product.objects.filter(status='active')
    inactive_products = Product.objects.filter(status='inactive')

    html = "<h1>🔍 Product Debug</h1>"
    html += f"<p><strong>Total products:</strong> {all_products.count()}</p>"
    html += f"<p><strong>Active products:</strong> {active_products.count()}</p>"
    html += f"<p><strong>Inactive products:</strong> {inactive_products.count()}</p>"

    html += "<h2>All Products:</h2><ul>"
    for p in all_products:
        status_color = "green" if p.status == 'active' else "red"
        html += f"<li style='color: {status_color};'>{p.title} - <strong>Status:</strong> {p.status} - <strong>Category:</strong> {p.category.name if p.category else 'None'} - <strong>Stock:</strong> {p.stock_quantity}</li>"
    html += "</ul>"

    html += "<h2>Categories:</h2><ul>"
    for c in Category.objects.all():
        product_count = c.products.filter(status='active').count()
        html += f"<li>{c.name} - <strong>Active products:</strong> {product_count}</li>"
    html += "</ul>"

    html += "<br><a href='/products/'>← Back to Products</a>"

    return HttpResponse(html)