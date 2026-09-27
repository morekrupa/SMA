/**
 * Design 2: Nordic Minimalist Studio Renderer
 * Tailored for Architectural Lighting, Clean Studio Presentation & High-Density Browsing
 */

window.NordicDesign = {
  name: "nordic",
  title: "Nordic Minimalist & Studio Lookbook",
  themeClass: "theme-nordic",

  renderCategories(categories, activeSlug) {
    const isAll = !activeSlug;
    let html = `
      <div class="nordic-filter-rail">
        <div class="nordic-filter-list">
          <button class="nordic-chip ${isAll ? 'active' : ''}" data-cat-slug="">
            ALL FIXTURES
          </button>
    `;

    categories.forEach(cat => {
      const active = (cat.slug === activeSlug) ? "active" : "";
      html += `
        <button class="nordic-chip ${active}" data-cat-slug="${cat.slug}" data-cat-id="${cat.id}">
          ${cat.name.toUpperCase()} (${cat.product_count})
        </button>
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
    const isInstock = product.stock_status === "instock";

    return `
      <div class="nordic-card" data-product-id="${product.id}" data-slug="${product.slug}">
        <div class="nordic-card-img-box" data-action="open-detail">
          <img class="nordic-card-img" 
               src="${product.thumbnail_url || product.cover_image}" 
               alt="${product.name}" 
               loading="lazy" 
               onerror="this.src='/static/images/placeholder.svg'" />

          <button class="nordic-select-badge ${isSelected ? 'selected' : ''}" 
                  title="${isSelected ? 'Remove from Selection' : 'Select for WhatsApp'}" 
                  data-action="toggle-select">
            ${isSelected ? '✓' : '＋'}
          </button>

          <button class="nordic-wish-badge ${isWishlisted ? 'active' : ''}" 
                  title="${isWishlisted ? 'Saved in Wishlist' : 'Add to Wishlist'}" 
                  data-action="toggle-wishlist">
            ${isWishlisted ? '♥' : '♡'}
          </button>
        </div>

        <div class="nordic-card-info">
          <span class="nordic-card-cat">${product.category_name}</span>
          <h3 class="nordic-card-title" data-action="open-detail">${product.name}</h3>
          <div class="nordic-card-price">
            ₹${product.price.toLocaleString('en-IN')}
            ${product.regular_price && product.regular_price > product.price ? 
              `<span style="color:#a1a1aa; font-weight:400; text-decoration:line-through; font-size:0.85em; margin-left:0.4rem;">₹${product.regular_price.toLocaleString('en-IN')}</span>` : ''}
          </div>
          <div class="nordic-card-actions">
            <button class="nordic-btn-action" data-action="open-detail">
              <span>EXPLORE</span>
            </button>
            <button class="nordic-btn-action nordic-btn-wa-direct" data-action="wa-single">
              <span>WHATSAPP</span>
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
        <div class="nordic-card" style="opacity: 0.7;">
          <div class="skeleton" style="width:100%; aspect-ratio:3/4; border-radius:2px;"></div>
          <div style="padding-top:1rem; display:flex; flex-direction:column; gap:0.4rem;">
            <div class="skeleton" style="height:12px; width:40%;"></div>
            <div class="skeleton" style="height:18px; width:80%;"></div>
            <div class="skeleton" style="height:14px; width:30%;"></div>
          </div>
        </div>
      `;
    }
    return html;
  }
};
