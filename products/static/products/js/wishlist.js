// ============================================
// Wishlist Page - Load items from localStorage
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Wishlist page loaded');
    
    // Get username
    const userElement = document.getElementById('current-username');
    const username = userElement ? userElement.dataset.username : 'guest';
    const key = 'eth_wishlist_' + username;
    
    let wishlistIds = [];
    
    try {
        const data = localStorage.getItem(key);
        if (data) {
            wishlistIds = JSON.parse(data);
            console.log('📋 Wishlist IDs:', wishlistIds);
        } else {
            console.log('📭 No wishlist found for user:', username);
        }
    } catch (e) {
        console.error('❌ Error loading wishlist:', e);
    }
    
    const container = document.getElementById('wishlistContainer');
    if (!container) {
        console.error('❌ Container not found');
        return;
    }
    
    if (!wishlistIds || wishlistIds.length === 0) {
        container.innerHTML = `
            <div class="col-span-full text-center py-12">
                <i class="fas fa-heart text-6xl text-gray-300 mb-4"></i>
                <p class="text-gray-500 text-lg">Your wishlist is empty</p>
                <p class="text-gray-400 text-sm">Start adding products you love by clicking the heart icon ❤️</p>
                <a href="/products/" class="btn btn-primary mt-4 inline-block">
                    <i class="fas fa-shopping-bag mr-2"></i> Start Shopping
                </a>
            </div>
        `;
        return;
    }
    
    // Show loading
    container.innerHTML = `
        <div class="col-span-full text-center py-8">
            <div class="spinner"></div>
            <p class="text-gray-500 mt-4">Loading your wishlist...</p>
        </div>
    `;
    
    // Fetch products using the wishlist API
    const idsParam = wishlistIds.join(',');
    const apiUrl = '/products/api/wishlist-products/?ids=' + encodeURIComponent(idsParam);
    
    console.log('🔄 Fetching from API:', apiUrl);
    
    fetch(apiUrl)
        .then(function(response) {
            if (!response.ok) {
                throw new Error('API request failed: ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            console.log('📦 API Response:', data);
            
            if (!data.products || data.products.length === 0) {
                container.innerHTML = `
                    <div class="col-span-full text-center py-12">
                        <i class="fas fa-heart text-6xl text-gray-300 mb-4"></i>
                        <p class="text-gray-500 text-lg">Your wishlist is empty</p>
                        <p class="text-gray-400 text-sm">Start adding products you love by clicking the heart icon ❤️</p>
                        <a href="/products/" class="btn btn-primary mt-4 inline-block">
                            <i class="fas fa-shopping-bag mr-2"></i> Start Shopping
                        </a>
                    </div>
                `;
                return;
            }
            
            let html = '';
            data.products.forEach(function(product) {
                const imageUrl = product.image_url || '/static/images/placeholder.svg';
                const price = Number(product.price).toLocaleString();
                
                html += `
                    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                        <div class="relative">
                            <img src="${imageUrl}" 
                                 alt="${product.title}" 
                                 class="w-full h-48 object-cover"
                                 onerror="this.src='/static/images/placeholder.svg'">
                            <button class="absolute top-2 right-2 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center text-red-500 hover:bg-red-50 transition-colors"
                                    onclick="removeFromWishlist(${product.id})"
                                    title="Remove from wishlist">
                                <i class="fas fa-heart"></i>
                            </button>
                        </div>
                        <div class="p-4">
                            <h3 class="font-semibold text-gray-900">${product.title}</h3>
                            <p class="text-sm text-gray-500">${product.source || 'Imported'}</p>
                            <p class="text-lg font-bold text-primary mt-2">ETB ${price}</p>
                            <a href="/products/product/${product.slug}/" class="mt-3 w-full btn btn-primary text-sm py-2 block text-center">
                                View Product
                            </a>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            console.log('✅ Wishlist loaded successfully');
        })
        .catch(function(error) {
            console.error('❌ Error fetching wishlist:', error);
            container.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <i class="fas fa-exclamation-circle text-4xl text-gray-300 mb-4"></i>
                    <p class="text-gray-500">Could not load wishlist items. Please try again.</p>
                    <p class="text-gray-400 text-sm">Error: ${error.message}</p>
                    <a href="/products/" class="btn btn-primary mt-4 inline-block">
                        <i class="fas fa-shopping-bag mr-2"></i> Start Shopping
                    </a>
                </div>
            `;
        });
});

// Make remove function globally accessible
window.removeFromWishlist = function(productId) {
    console.log('🗑️ Removing product:', productId);
    
    const userElement = document.getElementById('current-username');
    const username = userElement ? userElement.dataset.username : 'guest';
    const key = 'eth_wishlist_' + username;
    
    try {
        let wishlist = JSON.parse(localStorage.getItem(key) || '[]');
        wishlist = wishlist.filter(function(id) { 
            return parseInt(id) !== parseInt(productId); 
        });
        localStorage.setItem(key, JSON.stringify(wishlist));
        console.log('📋 Updated wishlist:', wishlist);
        
        // Update badge
        const badge = document.querySelector('.wishlist-badge');
        if (badge) {
            badge.textContent = wishlist.length;
            badge.style.display = wishlist.length > 0 ? 'flex' : 'none';
        }
        
        // Reload the page to refresh the wishlist
        location.reload();
    } catch (e) {
        console.error('❌ Error removing from wishlist:', e);
        alert('Error removing from wishlist. Please try again.');
    }
};