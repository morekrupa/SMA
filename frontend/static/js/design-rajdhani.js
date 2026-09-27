/**
 * Design 1: Lumina Ambient Studio Template Renderer
 * Reference style: rajdhanicarpets.com/?folder=rajdhani-digital-carpets
 * Adapted for Designer Table Lamps & Ambient Architectural Lighting
 */

window.RajdhaniDesign = {
  name: "rajdhani",
  title: "Lumina Ambient Showcase (Warm Gold & Glass)",
  themeClass: "theme-rajdhani",

  renderCategories(categories, activeSlug) {
    const isAll = !activeSlug;
    let html = `
      <div class="raj-folders-wrapper">
        <div class="raj-folders-container">
          <div class="raj-folder-pill ${isAll ? 'active' : ''}" data-cat-slug="">
            <span>💡 All Lighting</span>
          </div>
    `;

    categories.forEach(cat => {
      const active = (cat.slug === activeSlug) ? "active" : "";
      html += `
        <div class="raj-folder-pill ${active}" data-cat-slug="${cat.slug}" data-cat-id="${cat.id}">
          <span>💡 ${cat.name}</span>
          <span class="raj-folder-badge">${cat.product_count}</span>
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;
    return html;
  },

  renderProductCard(product) {
    const isSelected = window.whatsappManager && window.whatsappManager.isSelected(product.id);
    const isWishlisted = window.wishlist && window.wishlist.has(product.id);
    const hasDiscount = product.regular_price && product.regular_price > product.price;
    const isInstock = product.stock_status === "instock";

    return `
      <div class="raj-card" data-product-id="${product.id}" data-slug="${product.slug}">
        <button class="raj-select-trigger ${isSelected ? 'selected' : ''}" 
                title="${isSelected ? 'Deselect' : 'Select for WhatsApp Enquiry'}"
                data-action="toggle-select">
          ${isSelected ? '✓' : '＋'}
        </button>

        <button class="raj-wishlist-trigger ${isWishlisted ? 'active' : ''}" 
                title="${isWishlisted ? 'Remove from Wishlist' : 'Add to Wishlist'}" 
                data-action="toggle-wishlist">
          ${isWishlisted ? '♥' : '♡'}
        </button>

        <div class="raj-image-box" data-action="open-detail">
          <img class="raj-image" 
               src="${product.thumbnail_url || product.cover_image}" 
               alt="${product.name}" 
               loading="lazy" 
               onerror="this.src='/static/images/placeholder.svg'" />
          <div class="raj-zoom-hint" data-action="open-lightbox">
            <span>🔍 Zoom</span>
          </div>
        </div>

        <div class="raj-card-body">
          <div class="raj-category-tag">${product.category_name || 'Table Lamp'}</div>
          <h3 class="raj-title" data-action="open-detail">${product.name}</h3>

          <div class="raj-pricing">
            <span class="raj-price">₹${product.price.toLocaleString('en-IN')}</span>
            ${hasDiscount ? `<span class="raj-reg-price">₹${product.regular_price.toLocaleString('en-IN')}</span>` : ''}
            <span class="raj-stock-badge ${isInstock ? 'instock' : 'outofstock'}">
              ${isInstock ? 'In Stock' : 'Pre-Order'}
            </span>
          </div>

          <div class="raj-actions">
            <button class="raj-btn-view" data-action="open-detail">
              <span>View Specs</span>
            </button>
            <button class="raj-btn-wa" data-action="wa-single">
              <span>WhatsApp</span>
            </button>
          </div>
        </div>
      </div>
    `;
  },

  renderSkeletonGrid(count = 8) {
    let html = "";
    for (let i = 0; i < count; i++) {
      html += `
        <div class="skeleton-card">
          <div class="skeleton skeleton-img"></div>
          <div class="skeleton-body">
            <div class="skeleton skeleton-line short"></div>
            <div class="skeleton skeleton-line medium"></div>
            <div class="skeleton skeleton-line full"></div>
            <div class="skeleton skeleton-line short" style="margin-top:auto"></div>
          </div>
        </div>
      `;
    }
    return html;
  }
};
