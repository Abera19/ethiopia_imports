// ============================================
// ETH IMPORTS - Premium JavaScript
// ============================================

class ETHImportsApp {
    constructor() {
        this.wishlist = this.loadWishlist();
        this.cart = this.loadCart();
        this.isModalOpen = false;
        this.initialized = false;
        this.init();
    }

    init() {
        if (this.initialized) return;
        this.initialized = true;
        
        console.log('✅ ETH Imports App initialized');
        console.log('📋 Initial wishlist:', this.wishlist);
        
        this.setupHeaderScroll();
        this.setupSearch();
        this.setupMegaMenu();
        this.renderWishlistBadge();
        this.renderCartBadge();
        this.setupToast();
        this.setupModalClose();
        
        // Update all wishlist buttons after page loads
        setTimeout(() => {
            this.closeAllModals();
            this.updateAllWishlistButtons();
        }, 500);
    }

    closeAllModals() {
        document.querySelectorAll('.modal-overlay, #quickViewModal, #authModal, #cartModal').forEach(modal => {
            modal.style.display = 'none';
            modal.style.opacity = '0';
            modal.style.visibility = 'hidden';
            modal.style.pointerEvents = 'none';
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
        this.isModalOpen = false;
    }

    getUsername() {
        const userElement = document.getElementById('current-username');
        if (userElement) {
            return userElement.dataset.username || 'guest';
        }
        return 'guest';
    }

    setupHeaderScroll() {
        const header = document.getElementById('mainHeader');
        if (!header) return;
        
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const currentScroll = window.pageYOffset;
                    if (currentScroll > 50) {
                        header.classList.add('scrolled');
                    } else {
                        header.classList.remove('scrolled');
                    }
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    setupSearch() {
        const searchInput = document.getElementById('searchInput');
        const suggestions = document.getElementById('searchSuggestions');
        if (!searchInput) return;

        let debounceTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                const query = searchInput.value.trim();
                if (query.length < 2) {
                    suggestions.classList.remove('active');
                    return;
                }
                this.fetchSearchSuggestions(query);
            }, 300);
        });

        searchInput.addEventListener('focus', () => {
            if (searchInput.value.trim().length >= 2) {
                suggestions.classList.add('active');
            }
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    window.location.href = `/products/?q=${encodeURIComponent(query)}`;
                }
            }
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrapper')) {
                suggestions.classList.remove('active');
            }
        });
    }

    fetchSearchSuggestions(query) {
        const suggestions = document.getElementById('searchSuggestions');
        if (!suggestions) return;
        suggestions.innerHTML = `
            <div class="suggestion-item" onclick="window.location.href='/products/?q=${encodeURIComponent(query)}'">
                <i class="fas fa-search text-gray-400"></i>
                <span>Search for "${query}"</span>
            </div>
            <div class="suggestion-item">
                <i class="fas fa-clock text-gray-400"></i>
                <span>Recent: Ethiopian Coffee</span>
            </div>
            <div class="suggestion-item">
                <i class="fas fa-clock text-gray-400"></i>
                <span>Recent: Traditional Dress</span>
            </div>
        `;
        suggestions.classList.add('active');
    }

    setupMegaMenu() {
        const header = document.querySelector('.premium-header');
        const megaMenu = document.getElementById('megaMenu');
        if (!header || !megaMenu) return;
        let timeout;

        const openMenu = () => {
            clearTimeout(timeout);
            megaMenu.classList.add('open');
        };

        const closeMenu = () => {
            timeout = setTimeout(() => {
                megaMenu.classList.remove('open');
            }, 200);
        };

        header.addEventListener('mouseenter', openMenu);
        header.addEventListener('mouseleave', closeMenu);
        megaMenu.addEventListener('mouseenter', openMenu);
        megaMenu.addEventListener('mouseleave', closeMenu);
    }

    // ============================================
    // WISHLIST - COMPLETE FIXED VERSION
    // ============================================
    
    getWishlistKey() {
        return `eth_wishlist_${this.getUsername()}`;
    }

    loadWishlist() {
        try {
            const key = this.getWishlistKey();
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : [];
        } catch {
            return [];
        }
    }

    saveWishlist() {
        const key = this.getWishlistKey();
        localStorage.setItem(key, JSON.stringify(this.wishlist));
        this.renderWishlistBadge();
        // Update all buttons after saving
        setTimeout(() => {
            this.updateAllWishlistButtons();
        }, 100);
    }

    toggleWishlist(productId) {
        if (!productId) {
            this.showToast('Please log in to add to wishlist', 'warning');
            this.openAuthModal();
            return;
        }
        
        const index = this.wishlist.indexOf(productId);
        if (index > -1) {
            this.wishlist.splice(index, 1);
            this.showToast('Removed from wishlist 💔', 'info');
        } else {
            this.wishlist.push(productId);
            this.showToast('Added to wishlist ❤️', 'success');
        }
        this.saveWishlist();
        // Update UI immediately
        this.updateWishlistUI(productId);
        this.updateAllWishlistButtons();
        this.renderWishlistBadge();
    }

    renderWishlistBadge() {
        const badge = document.querySelector('.wishlist-badge');
        if (badge) {
            const count = this.wishlist.length;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    isInWishlist(productId) {
        return this.wishlist.includes(productId);
    }

    updateWishlistUI(productId) {
        // Find ALL elements with data-product-id matching
        const elements = document.querySelectorAll(`[data-product-id="${productId}"]`);
        
        elements.forEach(el => {
            // Only process if it's a button with heart icon
            if (el.classList.contains('wishlist-btn') || el.classList.contains('action-btn')) {
                const icon = el.querySelector('i');
                if (icon) {
                    if (this.isInWishlist(productId)) {
                        icon.className = 'fas fa-heart';
                        el.style.color = '#EF4444';
                        el.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
                    } else {
                        icon.className = 'far fa-heart';
                        el.style.color = '';
                        el.style.backgroundColor = '';
                    }
                }
            }
        });
    }

    updateAllWishlistButtons() {
        console.log('🔄 Updating all wishlist buttons');
        
        const wishlistIds = this.wishlist || [];
        console.log('📋 Current wishlist IDs:', wishlistIds);
        
        // Find all wishlist buttons with data-product-id
        const buttons = document.querySelectorAll('.wishlist-btn, .action-btn[data-product-id]');
        console.log('🔍 Found buttons:', buttons.length);
        
        buttons.forEach(btn => {
            const productId = parseInt(btn.dataset.productId);
            if (isNaN(productId)) return;
            
            const icon = btn.querySelector('i');
            if (!icon) return;
            
            if (wishlistIds.includes(productId)) {
                icon.className = 'fas fa-heart';
                btn.style.color = '#EF4444';
                btn.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
            } else {
                icon.className = 'far fa-heart';
                btn.style.color = '';
                btn.style.backgroundColor = '';
            }
        });
    }

    // ============================================
    // CART - COMPLETE
    // ============================================
    
    getCartKey() {
        return `eth_cart_${this.getUsername()}`;
    }

    loadCart() {
        try {
            const key = this.getCartKey();
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : [];
        } catch {
            return [];
        }
    }

    saveCart() {
        const key = this.getCartKey();
        localStorage.setItem(key, JSON.stringify(this.cart));
        this.renderCartBadge();
    }

    addToCart(productId, productTitle) {
        if (!productId) {
            this.showToast('Product ID not found', 'error');
            return;
        }
        const existing = this.cart.find(item => item.id === productId);
        const title = productTitle || 'Product';
        if (existing) {
            existing.quantity += 1;
            this.saveCart();
            this.showToast(`Updated ${title} in cart 🛒`, 'success');
        } else {
            let price = 0;
            const priceEl = document.querySelector('.text-3xl.font-bold.text-primary');
            if (priceEl) {
                const priceText = priceEl.textContent.replace(/[^0-9.]/g, '');
                price = parseFloat(priceText) || 0;
            }
            this.cart.push({ 
                id: productId, 
                quantity: 1,
                title: title,
                price: price
            });
            this.saveCart();
            this.showToast(`${title} added to cart 🛒`, 'success');
        }
    }

    renderCartBadge() {
        const badge = document.getElementById('cartBadge');
        if (badge) {
            const total = this.cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
            badge.textContent = total;
            badge.style.display = total > 0 ? 'flex' : 'none';
        }
    }

    showCart() {
        const modal = document.getElementById('cartModal');
        const content = document.getElementById('cartContent');
        if (!modal || !content) return;
        this.closeAllModals();
        if (this.cart.length === 0) {
            content.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-shopping-bag text-6xl text-gray-300 mb-4"></i>
                    <p class="text-gray-500">Your cart is empty</p>
                    <a href="/products/" class="btn btn-primary mt-4 inline-block">Start Shopping</a>
                </div>
            `;
        } else {
            let html = '<div class="space-y-4">';
            let total = 0;
            this.cart.forEach(item => {
                const itemTotal = (item.price || 0) * item.quantity;
                total += itemTotal;
                html += `
                    <div class="flex items-center gap-4 border-b border-gray-200 pb-4">
                        <div class="flex-1">
                            <h4 class="font-semibold text-gray-900">${item.title}</h4>
                            <p class="text-sm text-gray-500">ETB ${(item.price || 0).toLocaleString()}</p>
                            <div class="flex items-center gap-2 mt-1">
                                <button onclick="app.updateCartQuantity(${item.id}, ${item.quantity - 1})" class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50">-</button>
                                <span class="px-3">${item.quantity}</span>
                                <button onclick="app.updateCartQuantity(${item.id}, ${item.quantity + 1})" class="px-2 py-1 border border-gray-300 rounded hover:bg-gray-50">+</button>
                            </div>
                        </div>
                        <button onclick="app.removeFromCart(${item.id})" class="text-red-500 hover:text-red-700"><i class="fas fa-trash"></i></button>
                    </div>
                `;
            });
            html += `
                <div class="border-t border-gray-200 pt-4">
                    <div class="flex justify-between text-lg font-bold">
                        <span>Total:</span>
                        <span class="text-primary">ETB ${total.toLocaleString()}</span>
                    </div>
                    <button class="w-full btn btn-primary mt-4 py-3 text-lg" onclick="app.checkout()"><i class="fas fa-credit-card mr-2"></i> Proceed to Checkout</button>
                </div>
            </div>`;
            content.innerHTML = html;
        }
        
        modal.style.display = 'flex';
        modal.style.opacity = '1';
        modal.style.visibility = 'visible';
        modal.style.pointerEvents = 'auto';
        modal.style.position = 'fixed';
        modal.style.inset = '0';
        modal.style.background = 'rgba(0, 0, 0, 0.6)';
        modal.style.backdropFilter = 'blur(8px)';
        modal.style.webkitBackdropFilter = 'blur(8px)';
        modal.style.zIndex = '9999';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.padding = '1rem';
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        this.isModalOpen = true;
    }

    checkout() {
        this.showToast('Checkout feature coming soon! 🚀', 'info');
        this.closeCartModal();
    }

    closeCartModal() {
        this.closeModal('cartModal');
    }

    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
        this.showToast('Removed from cart', 'info');
        this.showCart();
    }

    updateCartQuantity(productId, quantity) {
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeFromCart(productId);
            } else {
                item.quantity = quantity;
                this.saveCart();
                this.showCart();
            }
        }
    }

    // ============================================
    // QUICK VIEW
    // ============================================
    
    async quickView(slug) {
        console.log('Quick View called for slug:', slug);
        
        if (!slug) {
            console.error('No slug provided');
            return;
        }
        
        if (this.isModalOpen) {
            console.log('Modal already open, ignoring request');
            return;
        }
        
        this.isModalOpen = true;
        
        try {
            const modal = document.getElementById('quickViewModal');
            const content = document.getElementById('quickViewContent');
            
            if (!modal || !content) {
                console.error('Modal or content not found');
                this.isModalOpen = false;
                return;
            }
            
            this.closeAllModals();
            
            content.innerHTML = `
                <div class="flex items-center justify-center py-12">
                    <div class="spinner"></div>
                </div>
            `;
            
            // FORCE OPEN WITH INLINE STYLES
            modal.style.display = 'flex';
            modal.style.opacity = '1';
            modal.style.visibility = 'visible';
            modal.style.pointerEvents = 'auto';
            modal.style.position = 'fixed';
            modal.style.inset = '0';
            modal.style.background = 'rgba(0, 0, 0, 0.6)';
            modal.style.backdropFilter = 'blur(8px)';
            modal.style.webkitBackdropFilter = 'blur(8px)';
            modal.style.zIndex = '9999';
            modal.style.alignItems = 'center';
            modal.style.justifyContent = 'center';
            modal.style.padding = '1rem';
            modal.classList.add('active');
            
            document.body.style.overflow = 'hidden';
            
            console.log('Modal opened with inline styles');
            
            const response = await fetch(`/products/api/quick-view/${slug}/`);
            if (!response.ok) throw new Error('Product not found');
            const product = await response.json();
            console.log('Product loaded:', product.title);
            
            const modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.style.display = 'block';
                modalContent.style.background = 'white';
                modalContent.style.borderRadius = '16px';
                modalContent.style.maxWidth = '720px';
                modalContent.style.width = '100%';
                modalContent.style.padding = '2rem';
                modalContent.style.boxShadow = '0 20px 60px rgba(0,0,0,0.3)';
                modalContent.style.maxHeight = '90vh';
                modalContent.style.overflowY = 'auto';
                modalContent.style.position = 'relative';
            }
            
            content.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6" style="width:100%;">
                    <div class="image-wrapper" style="padding-top: 75%; position: relative; background: #f0f2f5; border-radius: 12px; overflow: hidden;">
                        <img src="${product.image_url || '/static/images/placeholder.svg'}" 
                             alt="${product.title}"
                             style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;"
                             onerror="this.src='/static/images/placeholder.svg'">
                    </div>
                    <div>
                        <h3 class="text-xl font-bold mb-2">${product.title}</h3>
                        <p class="text-sm text-gray-500 mb-2">${product.source || 'Imported'}</p>
                        <p class="text-2xl font-bold text-primary mb-4">ETB ${Number(product.price).toLocaleString()}</p>
                        <p class="text-gray-600 mb-4">${product.description || 'Premium quality product'}</p>
                        <div class="flex items-center gap-2 mb-4">
                            <span class="text-sm ${product.in_stock ? 'text-green-600' : 'text-red-600'}">
                                ${product.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
                            </span>
                        </div>
                        <div class="flex gap-3">
                            <a href="/products/product/${slug}/" class="btn btn-primary flex-1" onclick="app.closeModal()">
                                View Details
                            </a>
                            <button class="btn btn-secondary" onclick="app.toggleWishlist(${product.id})" data-product-id="${product.id}">
                                <i class="${app.isInWishlist(product.id) ? 'fas' : 'far'} fa-heart"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
        } catch (error) {
            console.error('Quick view error:', error);
            const content = document.getElementById('quickViewContent');
            if (content) {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-exclamation-circle text-4xl text-red-500 mb-3"></i>
                        <p class="text-gray-600">Failed to load product details</p>
                        <button onclick="app.closeModal()" class="btn btn-primary mt-4">Close</button>
                    </div>
                `;
            }
            this.showToast('Failed to load product details', 'error');
        }
    }

    // ============================================
    // MODAL MANAGEMENT
    // ============================================
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId || 'quickViewModal');
        if (modal) {
            modal.style.display = 'none';
            modal.style.opacity = '0';
            modal.style.visibility = 'hidden';
            modal.style.pointerEvents = 'none';
            modal.classList.remove('active');
            document.body.style.overflow = '';
            this.isModalOpen = false;
        }
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            this.closeAllModals();
            modal.style.display = 'flex';
            modal.style.opacity = '1';
            modal.style.visibility = 'visible';
            modal.style.pointerEvents = 'auto';
            modal.style.position = 'fixed';
            modal.style.inset = '0';
            modal.style.background = 'rgba(0, 0, 0, 0.6)';
            modal.style.backdropFilter = 'blur(8px)';
            modal.style.webkitBackdropFilter = 'blur(8px)';
            modal.style.zIndex = '9999';
            modal.style.alignItems = 'center';
            modal.style.justifyContent = 'center';
            modal.style.padding = '1rem';
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            this.isModalOpen = true;
        }
    }

    closeAuthModal() {
        this.closeModal('authModal');
    }

    setupModalClose() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay') || 
                e.target.id === 'quickViewModal' || 
                e.target.id === 'authModal' || 
                e.target.id === 'cartModal') {
                const activeModals = document.querySelectorAll('.modal-overlay.active, #quickViewModal.active, #authModal.active, #cartModal.active');
                activeModals.forEach(modal => {
                    modal.style.display = 'none';
                    modal.style.opacity = '0';
                    modal.style.visibility = 'hidden';
                    modal.style.pointerEvents = 'none';
                    modal.classList.remove('active');
                });
                document.body.style.overflow = '';
                this.isModalOpen = false;
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const activeModals = document.querySelectorAll('.modal-overlay.active, #quickViewModal.active, #authModal.active, #cartModal.active');
                activeModals.forEach(modal => {
                    modal.style.display = 'none';
                    modal.style.opacity = '0';
                    modal.style.visibility = 'hidden';
                    modal.style.pointerEvents = 'none';
                    modal.classList.remove('active');
                });
                document.body.style.overflow = '';
                this.isModalOpen = false;
            }
        });
    }

    // ============================================
    // TOAST NOTIFICATIONS
    // ============================================
    
    setupToast() {
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.style.cssText = `
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                max-width: 380px;
            `;
            document.body.appendChild(container);
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const colors = { success: '#0F8B4C', error: '#EF4444', info: '#3B82F6', warning: '#F59E0B' };
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle', warning: 'fa-exclamation-triangle' };

        const toast = document.createElement('div');
        toast.style.cssText = `
            padding: 1rem 1.25rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border-left: 4px solid ${colors[type] || colors.info};
            animation: slideIn 0.3s ease;
            font-weight: 500;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        `;
        toast.innerHTML = `
            <i class="fas ${icons[type] || icons.info}" style="color: ${colors[type] || colors.info};"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" style="margin-left: auto; background: none; border: none; color: #9CA3AF; cursor: pointer; font-size: 1.1rem;">×</button>
        `;

        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // ============================================
    // AUTHENTICATION
    // ============================================
    
    openAuthModal() {
        const modal = document.getElementById('authModal');
        if (modal) {
            this.closeAllModals();
            modal.style.display = 'flex';
            modal.style.opacity = '1';
            modal.style.visibility = 'visible';
            modal.style.pointerEvents = 'auto';
            modal.style.position = 'fixed';
            modal.style.inset = '0';
            modal.style.background = 'rgba(0, 0, 0, 0.6)';
            modal.style.backdropFilter = 'blur(8px)';
            modal.style.webkitBackdropFilter = 'blur(8px)';
            modal.style.zIndex = '9999';
            modal.style.alignItems = 'center';
            modal.style.justifyContent = 'center';
            modal.style.padding = '1rem';
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            this.isModalOpen = true;
            this.showLogin();
        }
    }

    showLogin() {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        if (loginForm) loginForm.style.display = 'block';
        if (registerForm) registerForm.style.display = 'none';
    }

    showRegister() {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        if (loginForm) loginForm.style.display = 'none';
        if (registerForm) registerForm.style.display = 'block';
    }

    // ============================================
    // USER PROFILE METHODS
    // ============================================
    
    showProfile() {
        window.location.href = '/products/profile/';
    }

    showOrders() {
        window.location.href = '/products/orders/';
    }

    showWishlist() {
        window.location.href = '/products/wishlist/';
    }
}

// ============================================
// Initialize Application - Only Once
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    if (!window.app) {
        window.app = new ETHImportsApp();
        console.log('✅ App initialized successfully');
    } else {
        console.log('⚠️ App already initialized');
    }
});