// ============================================
// ETH Imports - Main Application JavaScript
// Complete functionality with state management
// ============================================

class ETHImportsApp {
    constructor() {
        this.state = {
            wishlist: this.loadWishlist(),
            filters: {
                search: '',
                category: '',
                minPrice: '',
                maxPrice: '',
                sort: '-created_at'
            },
            products: [],
            filteredProducts: [],
            currentPage: 1,
            isAuthenticated: false
        };
        
        this.init();
    }

    init() {
        this.loadProducts();
        this.setupEventListeners();
        this.renderWishlistBadge();
        this.setupAuthentication();
    }

    // ===== Wishlist Management =====
    loadWishlist() {
        try {
            return JSON.parse(localStorage.getItem('eth_imports_wishlist')) || [];
        } catch {
            return [];
        }
    }

    saveWishlist() {
        localStorage.setItem('eth_imports_wishlist', JSON.stringify(this.state.wishlist));
        this.renderWishlistBadge();
    }

    toggleWishlist(productId) {
        const index = this.state.wishlist.indexOf(productId);
        if (index > -1) {
            this.state.wishlist.splice(index, 1);
        } else {
            this.state.wishlist.push(productId);
        }
        this.saveWishlist();
        this.updateWishlistUI(productId);
        this.showToast(
            index > -1 ? 'Removed from wishlist' : 'Added to wishlist',
            index > -1 ? 'info' : 'success'
        );
    }

    isInWishlist(productId) {
        return this.state.wishlist.includes(productId);
    }

    renderWishlistBadge() {
        const badge = document.querySelector('.wishlist-badge');
        if (badge) {
            badge.textContent = this.state.wishlist.length;
            badge.style.display = this.state.wishlist.length > 0 ? 'flex' : 'none';
        }
    }

    updateWishlistUI(productId) {
        const heartBtn = document.querySelector(`[data-product-id="${productId}"] .wishlist-btn`);
        if (heartBtn) {
            const isWishlisted = this.isInWishlist(productId);
            heartBtn.classList.toggle('active', isWishlisted);
            heartBtn.innerHTML = isWishlisted 
                ? '<i class="fas fa-heart"></i>' 
                : '<i class="far fa-heart"></i>';
        }
    }

    // ===== Product Loading & Filtering =====
    async loadProducts() {
        try {
            const response = await fetch('/products/api/products/');
            this.state.products = await response.json();
            this.state.filteredProducts = [...this.state.products];
            this.renderProducts();
        } catch (error) {
            console.error('Failed to load products:', error);
            this.showToast('Failed to load products', 'error');
        }
    }

    applyFilters() {
        let filtered = [...this.state.products];
        const { search, category, minPrice, maxPrice, sort } = this.state.filters;

        // Search filter
        if (search.trim()) {
            const query = search.toLowerCase().trim();
            filtered = filtered.filter(p => 
                p.title.toLowerCase().includes(query) ||
                p.description.toLowerCase().includes(query) ||
                p.source.toLowerCase().includes(query)
            );
        }

        // Category filter
        if (category) {
            filtered = filtered.filter(p => p.category_slug === category);
        }

        // Price range filter
        if (minPrice) {
            filtered = filtered.filter(p => p.price >= parseFloat(minPrice));
        }
        if (maxPrice) {
            filtered = filtered.filter(p => p.price <= parseFloat(maxPrice));
        }

        // Sorting
        switch (sort) {
            case 'price':
                filtered.sort((a, b) => a.price - b.price);
                break;
            case '-price':
                filtered.sort((a, b) => b.price - a.price);
                break;
            case 'title':
                filtered.sort((a, b) => a.title.localeCompare(b.title));
                break;
            case '-title':
                filtered.sort((a, b) => b.title.localeCompare(a.title));
                break;
            default: // -created_at (newest first)
                filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        }

        this.state.filteredProducts = filtered;
        this.renderProducts();
        this.updateResultsCount();
    }

    renderProducts() {
        const grid = document.querySelector('.product-grid');
        if (!grid) return;

        if (this.state.filteredProducts.length === 0) {
            grid.innerHTML = `
                <div class="no-products">
                    <i class="fas fa-box-open" style="font-size: 3rem; color: var(--text-muted);"></i>
                    <h3>No products found</h3>
                    <p>Try adjusting your filters or search terms.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.state.filteredProducts.map(product => 
            this.createProductCard(product)
        ).join('');

        // Re-attach event listeners
        this.attachProductCardEvents();
    }

    createProductCard(product) {
        const isWishlisted = this.isInWishlist(product.id);
        const stockStatus = this.getStockStatus(product.stock_quantity);
        const stockBarClass = product.stock_quantity > 10 ? 'high' : 
                              product.stock_quantity > 0 ? 'medium' : 'low';
        const stockPercent = product.stock_quantity > 0 ? 100 : 0;

        return `
            <div class="product-card" data-product-id="${product.id}">
                <a href="/products/product/${product.slug}/" class="product-link">
                    <div class="product-card-image-wrapper">
                        <img src="${product.image || '/static/images/placeholder.png'}" 
                             alt="${product.title}" 
                             class="product-card-image"
                             loading="lazy"
                             onerror="this.src='/static/images/placeholder.png'">
                        <span class="stock-badge ${stockStatus.class}">
                            <span class="dot"></span>
                            ${stockStatus.label}
                        </span>
                    </div>
                </a>
                <div class="product-card-body">
                    <a href="/products/product/${product.slug}/" class="product-link">
                        <h3 class="product-card-title">${product.title}</h3>
                    </a>
                    <p class="product-card-source">${product.source}</p>
                    <p class="product-card-price">ETB ${Number(product.price).toLocaleString()}</p>
                    <div class="stock-bar-container">
                        <div class="stock-bar">
                            <div class="stock-bar-fill ${stockBarClass}" style="width: ${stockPercent}%"></div>
                        </div>
                        <span style="font-size: 0.75rem; color: var(--text-muted);">
                            ${product.stock_quantity} in stock
                        </span>
                    </div>
                    <button class="wishlist-btn ${isWishlisted ? 'active' : ''}" 
                            data-product-id="${product.id}"
                            onclick="app.toggleWishlist(${product.id})">
                        <i class="${isWishlisted ? 'fas' : 'far'} fa-heart"></i>
                    </button>
                </div>
            </div>
        `;
    }

    getStockStatus(quantity) {
        if (quantity === 0) return { label: 'Out of Stock', class: 'out-of-stock' };
        if (quantity <= 5) return { label: 'Low Stock', class: 'low-stock' };
        return { label: 'In Stock', class: 'in-stock' };
    }

    updateResultsCount() {
        const countEl = document.querySelector('.results-count');
        if (countEl) {
            countEl.textContent = `${this.state.filteredProducts.length} products found`;
        }
    }

    // ===== Event Listeners =====
    setupEventListeners() {
        // Filter form submission
        const filterForm = document.getElementById('filterForm');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.collectFilterValues();
                this.applyFilters();
                // Update URL without reload
                const params = new URLSearchParams(this.state.filters);
                window.history.pushState({}, '', `?${params.toString()}`);
            });
        }

        // Live search (optional - debounced)
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            let debounceTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimeout);
                debounceTimeout = setTimeout(() => {
                    this.state.filters.search = e.target.value;
                    this.applyFilters();
                }, 300);
            });
        }

        // Modal close
        document.querySelectorAll('.modal-close, .modal-overlay').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target === el || el.classList.contains('modal-close')) {
                    this.closeModal();
                }
            });
        });

        // Keyboard escape for modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
        });
    }

    collectFilterValues() {
        const form = document.getElementById('filterForm');
        if (!form) return;

        const formData = new FormData(form);
        this.state.filters = {
            search: formData.get('q') || '',
            category: formData.get('category') || '',
            minPrice: formData.get('min_price') || '',
            maxPrice: formData.get('max_price') || '',
            sort: formData.get('sort') || '-created_at'
        };
    }

    attachProductCardEvents() {
        // Quick view buttons
        document.querySelectorAll('.quick-view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const slug = btn.dataset.slug;
                this.openQuickView(slug);
            });
        });
    }

    // ===== Quick View =====
    async openQuickView(slug) {
        try {
            const response = await fetch(`/products/api/quick-view/${slug}/`);
            const product = await response.json();
            
            const modal = document.getElementById('quickViewModal');
            const content = document.getElementById('quickViewContent');
            
            content.innerHTML = `
                <div class="quick-view-grid">
                    <div class="quick-view-image">
                        <img src="${product.image_url || '/static/images/placeholder.png'}" 
                             alt="${product.title}"
                             onerror="this.src='/static/images/placeholder.png'">
                    </div>
                    <div class="quick-view-info">
                        <h2>${product.title}</h2>
                        <p class="price">ETB ${Number(product.price).toLocaleString()}</p>
                        <p class="description">${product.description}</p>
                        <div class="stock-status ${product.in_stock ? 'in-stock' : 'out-of-stock'}">
                            ${product.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
                        </div>
                        <div class="quick-view-actions">
                            <a href="/products/product/${slug}/" class="btn-primary">
                                View Details
                            </a>
                            <button class="btn-wishlist" onclick="app.toggleWishlist(${product.id})">
                                <i class="${this.isInWishlist(product.id) ? 'fas' : 'far'} fa-heart"></i>
                                ${this.isInWishlist(product.id) ? 'Remove from' : 'Add to'} Wishlist
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            this.openModal('quickViewModal');
        } catch (error) {
            console.error('Failed to load product details:', error);
            this.showToast('Failed to load product details', 'error');
        }
    }

    // ===== Modal Management =====
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }

    // ===== Authentication =====
    setupAuthentication() {
        const profileBtn = document.querySelector('.profile-btn');
        if (profileBtn) {
            profileBtn.addEventListener('click', () => {
                this.openAuthModal();
            });
        }
    }

    openAuthModal() {
        const modal = document.getElementById('authModal');
        if (modal) {
            this.openModal('authModal');
        } else {
            // Redirect to login if no modal
            window.location.href = '/accounts/login/';
        }
    }

    // ===== Toast Notifications =====
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) {
            // Create container if it doesn't exist
            const newContainer = document.createElement('div');
            newContainer.id = 'toastContainer';
            newContainer.style.cssText = `
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            `;
            document.body.appendChild(newContainer);
        }

        const toast = document.createElement('div');
        const colors = {
            success: '#0A8C5A',
            error: '#DC2626',
            info: '#3B82F6',
            warning: '#D97706'
        };

        toast.style.cssText = `
            padding: 1rem 1.5rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            border-left: 4px solid ${colors[type] || colors.info};
            animation: slideIn 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 500;
        `;
        toast.textContent = message;

        document.getElementById('toastContainer').appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ===== Pagination =====
    setupPagination(totalPages, currentPage) {
        const container = document.querySelector('.pagination');
        if (!container) return;

        let html = '';
        if (currentPage > 1) {
            html += `<button onclick="app.goToPage(${currentPage - 1})" class="page-btn">← Previous</button>`;
        }

        for (let i = 1; i <= totalPages; i++) {
            html += `<button onclick="app.goToPage(${i})" class="page-btn ${i === currentPage ? 'active' : ''}">${i}</button>`;
        }

        if (currentPage < totalPages) {
            html += `<button onclick="app.goToPage(${currentPage + 1})" class="page-btn">Next →</button>`;
        }

        container.innerHTML = html;
    }

    goToPage(page) {
        this.state.currentPage = page;
        // Fetch products for this page
        this.loadProducts();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// ============================================
// Initialize Application
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ETHImportsApp();
});

// ============================================
// Utility Functions
// ============================================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}