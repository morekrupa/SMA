/**
 * Catalog Maker - Core Frontend Orchestrator
 * High-speed mobile-first product catalog platform.
 */

(function () {
  "use strict";

  // Application State
  const state = {
    config: null,
    activeDesign: "rajdhani", // "rajdhani" | "nordic"
    activeDesignRenderer: window.RajdhaniDesign,
    categories: [],
    products: [],
    totalProducts: 0,
    currentPage: 1,
    pageSize: 16,
    hasMore: false,
    selectedCategorySlug: "",
    selectedCategoryId: "",
    searchQuery: "",
    sortBy: "featured",
    inStockOnly: false,
    activeProductDetail: null,
    isLoading: false,
  };

  // DOM Elements cache
  const elements = {};

  function initElements() {
    elements.announcement = document.getElementById("banner-announcement");
    elements.categoryNav = document.getElementById("category-nav-container");
    elements.productGrid = document.getElementById("product-grid");
    elements.searchInput = document.getElementById("search-input");
    elements.sortSelect = document.getElementById("sort-select");
    elements.totalCount = document.getElementById("total-count-badge");
    elements.loadMoreBtn = document.getElementById("load-more-btn");
    elements.detailModal = document.getElementById("product-detail-modal");
    elements.wishlistModal = document.getElementById("wishlist-modal");
    elements.wishlistBtn = document.getElementById("header-wishlist-btn");
    elements.wishlistCount = document.getElementById("header-wishlist-count");
    elements.waDock = document.getElementById("wa-dock");
    elements.waSendBtn = document.getElementById("wa-dock-send-btn");
    elements.waClearBtn = document.getElementById("wa-dock-clear-btn");
    elements.floatingWaBtn = document.getElementById("floating-wa-btn");
    elements.designSelector = document.getElementById("design-selector-select");
  }

  // --- INITIALIZATION ---
  async function init() {
    initElements();
    setupEventListeners();

    // Check URL params for design override or category filter
    const urlParams = new URLSearchParams(window.location.search);
    const designParam = urlParams.get("design");
    const categoryParam = urlParams.get("folder") || urlParams.get("category");

    if (categoryParam) {
      state.selectedCategorySlug = categoryParam;
    }

    // 1. Fetch store config
    try {
      state.config = await window.apiClient.getCatalogConfig();
      applyConfig(state.config, designParam);
    } catch (e) {
      console.error("Failed to load catalog config", e);
    }

    // 2. Fetch categories and render
    try {
      state.categories = await window.apiClient.getCategories();
      renderCategories();
    } catch (e) {
      console.error("Failed to load categories", e);
    }

    // 3. Initial product load
    await loadProducts(true);

    // 4. Update wishlist counters
    updateWishlistUI();

    // Check hash for direct product deep-link e.g. #product=shp_81001
    checkHashDeepLink();
  }

  function applyConfig(config, forcedDesign) {
    if (!config) return;

    // Set WhatsApp manager details
    window.whatsappManager.setWhatsAppNumber(config.whatsapp_number);
    window.whatsappManager.setTemplate(config.whatsapp_message_template);

    // Floating WhatsApp button link
    if (elements.floatingWaBtn) {
      const cleanNum = config.whatsapp_number.replace(/[^0-9]/g, "");
      elements.floatingWaBtn.href = `https://wa.me/${cleanNum}?text=${encodeURIComponent("Hello! I am browsing your catalog and would like to ask a question.")}`;
    }

    // Banner Announcement
    if (elements.announcement) {
      if (config.banner_is_active && config.banner_announcement) {
        elements.announcement.textContent = config.banner_announcement;
        elements.announcement.style.display = "block";
      } else {
        elements.announcement.style.display = "none";
      }
    }

    // Set Active Design
    const targetDesign = forcedDesign || config.active_design || "rajdhani";
    setActiveDesign(targetDesign);
  }

  function setActiveDesign(designName) {
    state.activeDesign = designName;
    if (designName === "nordic") {
      state.activeDesignRenderer = window.NordicDesign;
      document.body.className = "theme-nordic";
    } else {
      state.activeDesignRenderer = window.RajdhaniDesign;
      document.body.className = "theme-rajdhani";
    }

    if (elements.designSelector) {
      elements.designSelector.value = designName;
    }

    renderCategories();
    renderProducts();
  }

  // --- CATEGORIES ---
  function renderCategories() {
    if (!elements.categoryNav) return;
    elements.categoryNav.innerHTML = state.activeDesignRenderer.renderCategories(
      state.categories,
      state.selectedCategorySlug
    );
  }

  // --- PRODUCTS LOADING & RENDERING ---
  async function loadProducts(reset = false) {
    if (state.isLoading) return;
    state.isLoading = true;

    if (reset) {
      state.currentPage = 1;
      state.products = [];
      if (elements.productGrid) {
        elements.productGrid.innerHTML = state.activeDesignRenderer.renderSkeletonGrid(8);
      }
    }

    try {
      const response = await window.apiClient.getProducts({
        category_slug: state.selectedCategorySlug,
        search: state.searchQuery,
        sort: state.sortBy,
        in_stock_only: state.inStockOnly,
        page: state.currentPage,
        page_size: state.pageSize,
      });

      if (reset) {
        state.products = response.items;
      } else {
        state.products = state.products.concat(response.items);
      }

      state.totalProducts = response.total;
      state.hasMore = response.has_next;

      renderProducts();
      updateTotalCountUI();
    } catch (e) {
      console.error("Failed to load products", e);
      if (elements.productGrid && reset) {
        elements.productGrid.innerHTML = `
          <div style="grid-column: 1/-1; text-align:center; padding: 3rem 1rem;">
            <p style="font-size:1.1rem; font-weight:600; color:#ef4444;">Unable to load carpets</p>
            <p style="color:#64748b; font-size:0.9rem; margin-top:0.5rem;">Please check connection and retry</p>
            <button class="btn btn-outline" style="margin-top:1rem;" onclick="location.reload()">Retry</button>
          </div>
        `;
      }
    } finally {
      state.isLoading = false;
    }
  }

  function renderProducts() {
    if (!elements.productGrid) return;

    if (state.products.length === 0) {
      elements.productGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem;">
          <div style="font-size: 3rem; margin-bottom: 0.5rem;">🔍</div>
          <h3 style="font-size: 1.25rem; font-weight: 700; color: #1e293b;">No Carpets Found</h3>
          <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.25rem;">
            Try clearing filters or searching with a different term.
          </p>
          <button class="btn btn-outline" style="margin-top: 1rem;" id="reset-filters-btn">
            Clear Filters & Search
          </button>
        </div>
      `;
      const resetBtn = document.getElementById("reset-filters-btn");
      if (resetBtn) {
        resetBtn.addEventListener("click", () => {
          state.selectedCategorySlug = "";
          state.searchQuery = "";
          if (elements.searchInput) elements.searchInput.value = "";
          renderCategories();
          loadProducts(true);
        });
      }
      if (elements.loadMoreBtn) elements.loadMoreBtn.style.display = "none";
      return;
    }

    elements.productGrid.innerHTML = state.products
      .map((p) => state.activeDesignRenderer.renderProductCard(p))
      .join("");

    if (elements.loadMoreBtn) {
      elements.loadMoreBtn.style.display = state.hasMore ? "inline-flex" : "none";
    }
  }

  function updateTotalCountUI() {
    if (elements.totalCount) {
      elements.totalCount.textContent = `${state.totalProducts} Carpets`;
    }
  }

  // --- PRODUCT POP-UP / DETAIL MODAL ---
  async function openProductDetail(idOrSlug) {
    try {
      const modal = elements.detailModal;
      if (!modal) return;

      // Show skeleton in modal while loading
      const modalContent = modal.querySelector(".modal-body");
      modalContent.innerHTML = `
        <div style="padding: 1rem; display: flex; flex-direction: column; gap: 1rem;">
          <div class="skeleton" style="width: 100%; height: 320px; border-radius: 8px;"></div>
          <div class="skeleton" style="height: 24px; width: 60%;"></div>
          <div class="skeleton" style="height: 16px; width: 40%;"></div>
          <div class="skeleton" style="height: 80px; width: 100%;"></div>
        </div>
      `;
      modal.classList.add("active");
      document.body.style.overflow = "hidden";

      const product = await window.apiClient.getProductDetail(idOrSlug);
      state.activeProductDetail = product;

      // Track analytics
      window.apiClient.recordAnalytics("product_view", product.id, { name: product.name });

      // Render modal body
      const isSelected = window.whatsappManager.isSelected(product.id);
      const isWishlisted = window.wishlist.has(product.id);
      const isInstock = product.stock_status === "instock";

      modalContent.innerHTML = `
        <div class="product-modal-inner">
          <!-- Gallery -->
          <div class="modal-gallery" style="position:relative;">
            <img id="modal-main-img" 
                 src="${product.images[0] ? product.images[0].url : '/static/images/placeholder.svg'}" 
                 alt="${product.name}" 
                 style="width:100%; height:340px; object-fit:cover; border-radius:8px; cursor:zoom-in; background:#f1f5f9;" 
                 onerror="this.src='/static/images/placeholder.svg'" />
            <button class="btn btn-outline" id="modal-zoom-btn" 
                    style="position:absolute; bottom:12px; right:12px; background:rgba(0,0,0,0.6); color:white; border:none; padding:0.35rem 0.75rem; border-radius:6px; font-size:0.8rem; backdrop-filter:blur(4px);">
              🔍 Full Lightbox
            </button>
          </div>

          <!-- Thumbnail Strip -->
          ${product.images.length > 1 ? `
            <div style="display:flex; gap:0.5rem; margin-top:0.75rem; overflow-x:auto; padding-bottom:0.25rem;">
              ${product.images.map((img, idx) => `
                <img class="modal-thumb ${idx === 0 ? 'active' : ''}" 
                     data-idx="${idx}" 
                     src="${img.thumbnail_url || img.url}" 
                     alt="thumb" 
                     style="width:60px; height:60px; object-fit:cover; border-radius:6px; cursor:pointer; border:2px solid ${idx === 0 ? '#b45309' : '#e2e8f0'};" />
              `).join("")}
            </div>
          ` : ""}

          <!-- Info -->
          <div style="margin-top:1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;">
              <div>
                <span style="font-size:0.75rem; font-weight:700; color:#b45309; text-transform:uppercase; letter-spacing:0.05em;">
                  ${product.category_name}
                </span>
                <h2 style="font-size:1.35rem; font-weight:800; color:#0f172a; margin-top:0.2rem; line-height:1.3;">
                  ${product.name}
                </h2>
                <div style="font-size:0.8rem; color:#64748b; margin-top:0.2rem;">SKU: ${product.sku}</div>
              </div>
              <button id="modal-wish-btn" 
                      style="background:#f8fafc; border:1px solid #e2e8f0; width:44px; height:44px; border-radius:10px; cursor:pointer; font-size:1.25rem; color:${isWishlisted ? '#ef4444' : '#64748b'}; display:flex; align-items:center; justify-content:center;">
                ${isWishlisted ? '♥' : '♡'}
              </button>
            </div>

            <!-- Price & Availability -->
            <div style="display:flex; align-items:baseline; gap:0.6rem; margin:1rem 0; padding:0.75rem; background:#f8fafc; border-radius:8px;">
              <span id="modal-price" style="font-size:1.4rem; font-weight:800; color:#0f172a;">
                ₹${product.price.toLocaleString('en-IN')}
              </span>
              ${product.regular_price && product.regular_price > product.price ? `
                <span id="modal-regular-price" style="font-size:0.95rem; color:#94a3b8; text-decoration:line-through;">
                  ₹${product.regular_price.toLocaleString('en-IN')}
                </span>
              ` : ""}
              <span style="margin-left:auto; font-size:0.75rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:4px; ${isInstock ? 'background:#dcfce7; color:#15803d;' : 'background:#fee2e2; color:#991b1b;'}">
                ${isInstock ? 'Ready to Ship' : 'Made to Order'}
              </span>
            </div>

            <!-- Variants / Sizes -->
            ${product.variants && product.variants.length > 0 ? `
              <div style="margin-bottom:1.25rem;">
                <label style="font-size:0.85rem; font-weight:700; color:#334155; display:block; margin-bottom:0.4rem;">
                  Available Sizes & Dimensions:
                </label>
                <div style="display:flex; flex-wrap:wrap; gap:0.5rem;" id="modal-variant-options">
                  ${product.variants.map((v, i) => `
                    <button class="btn btn-outline modal-var-btn ${i === 0 ? 'btn-primary' : ''}" 
                            data-var-idx="${i}" 
                            data-price="${v.price}"
                            data-reg-price="${v.regular_price || ''}"
                            style="font-size:0.825rem; padding:0.4rem 0.8rem; min-height:36px;">
                      ${v.title} (₹${v.price.toLocaleString('en-IN')})
                    </button>
                  `).join("")}
                </div>
              </div>
            ` : ""}

            <!-- Description -->
            <div style="margin-bottom:1.25rem;">
              <h4 style="font-size:0.9rem; font-weight:700; color:#1e293b; margin-bottom:0.4rem;">Artisan Description</h4>
              <div style="font-size:0.9rem; color:#475569; line-height:1.6;">
                ${product.description || product.short_description}
              </div>
            </div>

            <!-- Specifications Table -->
            <div style="margin-bottom:1.5rem;">
              <h4 style="font-size:0.9rem; font-weight:700; color:#1e293b; margin-bottom:0.5rem;">Specifications</h4>
              <table style="width:100%; border-collapse:collapse; font-size:0.85rem;">
                <tbody>
                  ${Object.entries(product.metadata).map(([k, v]) => `
                    <tr style="border-bottom:1px solid #f1f5f9;">
                      <td style="padding:0.45rem 0; color:#64748b; font-weight:500; text-transform:capitalize;">${k.replace(/_/g, ' ')}</td>
                      <td style="padding:0.45rem 0; text-align:right; font-weight:600; color:#0f172a;">${v}</td>
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>

            <!-- Action Buttons -->
            <div style="display:flex; gap:0.75rem; position:sticky; bottom:0; background:white; padding-top:0.75rem; border-top:1px solid #e2e8f0;">
              <button class="btn btn-whatsapp" id="modal-wa-btn" style="flex:2;">
                <span>💬 Enquire on WhatsApp</span>
              </button>
              <button class="btn btn-outline" id="modal-select-btn" style="flex:1;">
                <span>${isSelected ? '✓ Selected' : '＋ Select'}</span>
              </button>
            </div>
          </div>
        </div>
      `;

      // Bind modal internal events
      bindModalEvents(product);
    } catch (e) {
      console.error("Failed to load product detail", e);
      closeProductDetail();
    }
  }

  function bindModalEvents(product) {
    const modal = elements.detailModal;
    if (!modal) return;

    // Zoom Lightbox
    const mainImg = modal.querySelector("#modal-main-img");
    const zoomBtn = modal.querySelector("#modal-zoom-btn");
    const thumbs = modal.querySelectorAll(".modal-thumb");

    const openLb = () => {
      const activeSrc = mainImg.src;
      let startIdx = 0;
      product.images.forEach((img, idx) => {
        if (img.url === activeSrc) startIdx = idx;
      });
      window.lightbox.open(product.images, startIdx);
    };

    if (mainImg) mainImg.addEventListener("click", openLb);
    if (zoomBtn) zoomBtn.addEventListener("click", openLb);

    // Thumb click
    thumbs.forEach((th) => {
      th.addEventListener("click", () => {
        thumbs.forEach((t) => (t.style.borderColor = "#e2e8f0"));
        th.style.borderColor = "#b45309";
        const idx = parseInt(th.dataset.idx, 10);
        if (product.images[idx]) {
          mainImg.src = product.images[idx].url;
        }
      });
    });

    // Variants toggle
    const varButtons = modal.querySelectorAll(".modal-var-btn");
    varButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        varButtons.forEach((b) => b.classList.remove("btn-primary"));
        btn.classList.add("btn-primary");
        const price = parseFloat(btn.dataset.price);
        const modalPrice = modal.querySelector("#modal-price");
        if (modalPrice) modalPrice.textContent = `₹${price.toLocaleString("en-IN")}`;
      });
    });

    // Single WhatsApp enquiry
    const waBtn = modal.querySelector("#modal-wa-btn");
    if (waBtn) {
      waBtn.addEventListener("click", () => {
        window.whatsappManager.sendSingleEnquiry(product);
      });
    }

    // Modal selection toggle
    const selBtn = modal.querySelector("#modal-select-btn");
    if (selBtn) {
      selBtn.addEventListener("click", () => {
        window.whatsappManager.toggleSelect(product);
        const isSel = window.whatsappManager.isSelected(product.id);
        selBtn.innerHTML = `<span>${isSel ? "✓ Selected" : "＋ Select"}</span>`;
        renderProducts(); // refresh card checkmarks
      });
    }

    // Modal Wishlist toggle
    const wishBtn = modal.querySelector("#modal-wish-btn");
    if (wishBtn) {
      wishBtn.addEventListener("click", () => {
        const added = window.wishlist.toggle(product);
        wishBtn.innerHTML = added ? "♥" : "♡";
        wishBtn.style.color = added ? "#ef4444" : "#64748b";
        updateWishlistUI();
        renderProducts(); // refresh card hearts
      });
    }
  }

  function closeProductDetail() {
    if (elements.detailModal) {
      elements.detailModal.classList.remove("active");
      document.body.style.overflow = "";
    }
  }

  // --- WISHLIST DRAWER MODAL ---
  function openWishlistModal() {
    const modal = elements.wishlistModal;
    if (!modal) return;

    const items = window.wishlist.getItems();
    const body = modal.querySelector(".modal-body");

    if (items.length === 0) {
      body.innerHTML = `
        <div style="text-align:center; padding:3rem 1rem;">
          <div style="font-size:2.5rem; margin-bottom:0.5rem;">♡</div>
          <h3 style="font-size:1.15rem; font-weight:700;">Your Wishlist is Empty</h3>
          <p style="color:#64748b; font-size:0.9rem; margin-top:0.25rem;">
            Tap the heart icon on any carpet to save it for later.
          </p>
        </div>
      `;
    } else {
      body.innerHTML = `
        <div>
          <div style="display:flex; flex-direction:column; gap:0.75rem; margin-bottom:1.5rem;">
            ${items.map((it) => `
              <div style="display:flex; align-items:center; gap:0.75rem; padding:0.5rem; border:1px solid #e2e8f0; border-radius:8px;">
                <img src="${it.cover_image}" alt="${it.name}" style="width:50px; height:50px; object-fit:cover; border-radius:6px;" onerror="this.src='/static/images/placeholder.svg'"/>
                <div style="flex:1; min-width:0;">
                  <h4 style="font-size:0.875rem; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${it.name}</h4>
                  <div style="font-size:0.8rem; color:#b45309; font-weight:700;">₹${it.price.toLocaleString("en-IN")}</div>
                </div>
                <button class="remove-wish-item-btn" data-id="${it.id}" style="background:none; border:none; color:#ef4444; font-size:1.2rem; cursor:pointer; padding:0.4rem;">✕</button>
              </div>
            `).join("")}
          </div>

          <div style="display:flex; flex-direction:column; gap:0.5rem;">
            <button class="btn btn-whatsapp" id="send-wishlist-wa-btn" style="width:100%;">
              <span>💬 Enquire All ${items.length} Carpets on WhatsApp</span>
            </button>
            <button class="btn btn-outline" id="clear-wishlist-btn" style="width:100%;">
              Clear Wishlist
            </button>
          </div>
        </div>
      `;

      // Event handlers for wishlist items
      body.querySelectorAll(".remove-wish-item-btn").forEach((b) => {
        b.addEventListener("click", () => {
          window.wishlist.remove(b.dataset.id);
          openWishlistModal();
          updateWishlistUI();
          renderProducts();
        });
      });

      const sendWaBtn = body.querySelector("#send-wishlist-wa-btn");
      if (sendWaBtn) {
        sendWaBtn.addEventListener("click", () => {
          window.whatsappManager.sendWishlistEnquiry(items);
        });
      }

      const clearBtn = body.querySelector("#clear-wishlist-btn");
      if (clearBtn) {
        clearBtn.addEventListener("click", () => {
          window.wishlist.clear();
          openWishlistModal();
          updateWishlistUI();
          renderProducts();
        });
      }
    }

    modal.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  function closeWishlistModal() {
    if (elements.wishlistModal) {
      elements.wishlistModal.classList.remove("active");
      document.body.style.overflow = "";
    }
  }

  function updateWishlistUI() {
    const count = window.wishlist.getCount();
    if (elements.wishlistCount) {
      elements.wishlistCount.textContent = count;
      elements.wishlistCount.style.display = count > 0 ? "flex" : "none";
    }
  }

  // --- HASH ROUTING FOR DEEP-LINKING ---
  function checkHashDeepLink() {
    const hash = window.location.hash;
    if (hash.startsWith("#product=")) {
      const prodId = hash.replace("#product=", "");
      if (prodId) openProductDetail(prodId);
    }
  }

  // --- EVENT LISTENERS ---
  function setupEventListeners() {
    // Category pill clicks (Delegated)
    if (elements.categoryNav) {
      elements.categoryNav.addEventListener("click", (e) => {
        const pill = e.target.closest("[data-cat-slug]");
        if (!pill) return;
        state.selectedCategorySlug = pill.dataset.catSlug || "";
        renderCategories();
        loadProducts(true);
      });
    }

    // Debounced Search Input
    if (elements.searchInput) {
      let debounceTimer = null;
      elements.searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          state.searchQuery = e.target.value.trim();
          loadProducts(true);
        }, 250);
      });
    }

    // Sort Dropdown
    if (elements.sortSelect) {
      elements.sortSelect.addEventListener("change", (e) => {
        state.sortBy = e.target.value;
        loadProducts(true);
      });
    }

    // Load More Button
    if (elements.loadMoreBtn) {
      elements.loadMoreBtn.addEventListener("click", () => {
        state.currentPage += 1;
        loadProducts(false);
      });
    }

    // Design Switcher in Header/Controls
    if (elements.designSelector) {
      elements.designSelector.addEventListener("change", (e) => {
        setActiveDesign(e.target.value);
      });
    }

    // Wishlist Open
    if (elements.wishlistBtn) {
      elements.wishlistBtn.addEventListener("click", openWishlistModal);
    }

    // Detail Modal Close
    if (elements.detailModal) {
      const closeBtn = elements.detailModal.querySelector(".modal-close-btn");
      if (closeBtn) closeBtn.addEventListener("click", closeProductDetail);
      elements.detailModal.addEventListener("click", (e) => {
        if (e.target === elements.detailModal) closeProductDetail();
      });
    }

    // Wishlist Modal Close
    if (elements.wishlistModal) {
      const closeBtn = elements.wishlistModal.querySelector(".modal-close-btn");
      if (closeBtn) closeBtn.addEventListener("click", closeWishlistModal);
      elements.wishlistModal.addEventListener("click", (e) => {
        if (e.target === elements.wishlistModal) closeWishlistModal();
      });
    }

    // WhatsApp Dock Actions
    if (elements.waSendBtn) {
      elements.waSendBtn.addEventListener("click", () => {
        window.whatsappManager.sendMultiEnquiry();
      });
    }

    if (elements.waClearBtn) {
      elements.waClearBtn.addEventListener("click", () => {
        window.whatsappManager.clearSelection();
        renderProducts();
      });
    }

    // Product Grid Delegated Clicks (Select, Wishlist, Open, WhatsApp)
    if (elements.productGrid) {
      elements.productGrid.addEventListener("click", (e) => {
        const card = e.target.closest("[data-product-id]");
        if (!card) return;

        const prodId = card.dataset.productId;
        const product = state.products.find((p) => p.id === prodId);
        if (!product) return;

        const actionTarget = e.target.closest("[data-action]");
        const action = actionTarget ? actionTarget.dataset.action : "open-detail";

        if (action === "toggle-select") {
          e.stopPropagation();
          window.whatsappManager.toggleSelect(product);
          actionTarget.classList.toggle("selected");
          actionTarget.innerHTML = window.whatsappManager.isSelected(product.id) ? "✓" : "＋";
        } else if (action === "toggle-wishlist") {
          e.stopPropagation();
          const added = window.wishlist.toggle(product);
          actionTarget.classList.toggle("active", added);
          actionTarget.innerHTML = added ? "♥" : "♡";
          updateWishlistUI();
        } else if (action === "wa-single") {
          e.stopPropagation();
          window.whatsappManager.sendSingleEnquiry(product);
        } else if (action === "open-lightbox") {
          e.stopPropagation();
          window.lightbox.open([product.cover_image], 0);
        } else {
          // Open detail popup
          openProductDetail(product.id);
        }
      });
    }

    // Listen to hash changes (e.g. back button)
    window.addEventListener("hashchange", checkHashDeepLink);

    // Listen for wishlist updates
    window.addEventListener("wishlist:updated", updateWishlistUI);
  }

  // Auto-boot on DOM ready
  document.addEventListener("DOMContentLoaded", init);
})();
