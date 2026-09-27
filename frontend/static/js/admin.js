/**
 * Catalog Maker - Admin Dashboard Single-Page Application
 * Handles products CRUD, categories, quick inline pricing/stock adjustments,
 * Shopify & WooCommerce sync triggers, audit log, and live source simulation.
 */

(function () {
  "use strict";

  const admin = {
    activeTab: "overview",
    stats: {},
    products: [],
    categories: [],
    syncLogs: [],
    auditLogs: [],
    settings: {},
    page: 1,
    pageSize: 20,
    totalPages: 1,
    search: "",
    sourceFilter: "",
    categoryFilter: ""
  };

  document.addEventListener("DOMContentLoaded", initAdmin);

  async function initAdmin() {
    setupTabNavigation();
    setupSyncControls();
    setupSettingsForm();
    setupProductForm();
    setupCategoryForm();
    setupSimulationTools();
    
    // Load initial data
    await refreshStats();
    await loadSettings();
    await loadProducts();
    await loadCategories();
    await loadSyncHistory();
    await loadAuditLog();
  }

  // --- NAVIGATION ---
  function setupTabNavigation() {
    const navItems = document.querySelectorAll(".admin-nav-item");
    navItems.forEach(item => {
      item.addEventListener("click", () => {
        const tab = item.dataset.tab;
        if (!tab) return;
        navItems.forEach(n => n.classList.remove("active"));
        item.classList.add("active");
        
        document.querySelectorAll(".tab-view").forEach(v => v.style.display = "none");
        const targetView = document.getElementById(`tab-view-${tab}`);
        if (targetView) targetView.style.display = "block";
        admin.activeTab = tab;

        if (tab === "overview") refreshStats();
        if (tab === "products") loadProducts();
        if (tab === "categories") loadCategories();
        if (tab === "sync") loadSyncHistory();
        if (tab === "audit") loadAuditLog();
        if (tab === "settings") loadSettings();
      });
    });
  }

  // --- STATS OVERVIEW ---
  async function refreshStats() {
    try {
      const resp = await fetch("/api/v1/admin/stats");
      const data = await resp.json();
      admin.stats = data;

      document.getElementById("stat-total-products").textContent = data.total_products;
      document.getElementById("stat-active-products").textContent = data.active_products;
      document.getElementById("stat-shopify-synced").textContent = data.shopify_products;
      document.getElementById("stat-wc-synced").textContent = data.woocommerce_products;
      document.getElementById("stat-wa-enquiries").textContent = data.whatsapp_enquiries;
      document.getElementById("stat-prod-views").textContent = data.product_views;

      renderRecentSyncs(data.recent_syncs || []);
    } catch (e) {
      console.error("Failed to load stats", e);
    }
  }

  function renderRecentSyncs(syncs) {
    const tbody = document.getElementById("overview-recent-syncs-tbody");
    if (!tbody) return;
    if (syncs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:1.5rem; color:#94a3b8;">No sync operations recorded yet.</td></tr>`;
      return;
    }
    tbody.innerHTML = syncs.map(s => `
      <tr>
        <td><strong>#${s.id.substring(0, 8)}</strong></td>
        <td><span class="badge badge-source-${s.source === 'shopify' ? 'shopify' : 'wc'}">${s.source.toUpperCase()}</span></td>
        <td><span style="color:${s.status === 'success' ? '#10b981' : '#ef4444'}; font-weight:700;">${s.status.toUpperCase()}</span></td>
        <td>${s.items_fetched}</td>
        <td>+${s.items_created} new, ~${s.items_updated} updated</td>
        <td>${s.duration_ms}ms</td>
      </tr>
    `).join("");
  }

  // --- PRODUCTS CRUD & INLINE EDITING ---
  async function loadProducts() {
    try {
      const params = new URLSearchParams({
        page: admin.page,
        page_size: admin.pageSize
      });
      if (admin.search) params.set("search", admin.search);
      if (admin.sourceFilter) params.set("source", admin.sourceFilter);
      if (admin.categoryFilter) params.set("category_id", admin.categoryFilter);

      const resp = await fetch(`/api/v1/admin/products?${params.toString()}`);
      const data = await resp.json();
      admin.products = data.items;
      admin.totalPages = data.total_pages;

      renderProductsTable(data.items);
      document.getElementById("products-pagination-info").textContent = `Page ${data.page} of ${data.total_pages} (${data.total} total items)`;
      document.getElementById("btn-prev-page").disabled = (admin.page <= 1);
      document.getElementById("btn-next-page").disabled = (admin.page >= admin.totalPages);
    } catch (e) {
      console.error("Failed to load products", e);
    }
  }

  function renderProductsTable(items) {
    const tbody = document.getElementById("admin-products-tbody");
    if (!tbody) return;

    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:2rem; color:#94a3b8;">No products found matching criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(p => {
      const isInstock = p.stock_status === "instock";
      const badgeClass = p.source === "shopify" ? "badge-source-shopify" : (p.source === "woocommerce" ? "badge-source-wc" : "badge-source-manual");

      return `
        <tr data-id="${p.id}">
          <td>
            <img class="table-img" src="${p.cover_image}" alt="thumb" onerror="this.src='/static/images/placeholder.svg'" />
          </td>
          <td>
            <div style="font-weight:700; color:#0f172a;">${p.name}</div>
            <div style="font-size:0.75rem; color:#64748b;">SKU: ${p.sku} | <span class="badge ${badgeClass}">${p.source}</span></div>
          </td>
          <td>
            <span style="font-size:0.8rem; color:#475569;">${p.category_name || '-'}</span>
          </td>
          <td>
            <div style="display:flex; align-items:center; gap:0.25rem;">
              <span style="color:#64748b; font-size:0.8rem;">₹</span>
              <input type="number" class="inline-price-input" data-id="${p.id}" value="${p.price}" />
              <button class="btn btn-outline btn-save-price" data-id="${p.id}" style="min-height:28px; padding:0.15rem 0.4rem; font-size:0.75rem;">Save</button>
            </div>
          </td>
          <td>
            <label class="toggle-switch">
              <input type="checkbox" class="toggle-stock" data-id="${p.id}" ${isInstock ? 'checked' : ''} />
              <span class="slider"></span>
            </label>
            <span style="font-size:0.75rem; margin-left:0.35rem; color:${isInstock ? '#166534' : '#991b1b'}; font-weight:600;">
              ${isInstock ? 'In Stock' : 'Out'}
            </span>
          </td>
          <td>
            <label class="toggle-switch">
              <input type="checkbox" class="toggle-active" data-id="${p.id}" ${p.is_active ? 'checked' : ''} />
              <span class="slider"></span>
            </label>
          </td>
          <td>
            <div style="display:flex; gap:0.4rem;">
              <button class="btn btn-outline btn-edit-product" data-id="${p.id}" style="min-height:30px; padding:0.2rem 0.6rem; font-size:0.75rem;">Edit</button>
              <button class="btn btn-outline btn-delete-product" data-id="${p.id}" style="min-height:30px; padding:0.2rem 0.6rem; font-size:0.75rem; color:#ef4444;">Delete</button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

    bindProductTableEvents();
  }

  function bindProductTableEvents() {
    // Quick price save
    document.querySelectorAll(".btn-save-price").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        const input = document.querySelector(`.inline-price-input[data-id="${id}"]`);
        const newPrice = parseFloat(input.value);
        if (isNaN(newPrice)) return;
        btn.textContent = "...";
        try {
          const res = await fetch(`/api/v1/admin/products/${id}/quick-update`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ price: newPrice })
          });
          if (res.ok) {
            btn.textContent = "Saved!";
            setTimeout(() => btn.textContent = "Save", 1500);
            refreshStats();
          }
        } catch (e) {
          btn.textContent = "Error";
        }
      });
    });

    // Quick stock toggle
    document.querySelectorAll(".toggle-stock").forEach(chk => {
      chk.addEventListener("change", async () => {
        const id = chk.dataset.id;
        const newStatus = chk.checked ? "instock" : "outofstock";
        await fetch(`/api/v1/admin/products/${id}/quick-update`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stock_status: newStatus, stock_quantity: chk.checked ? 5 : 0 })
        });
        refreshStats();
      });
    });

    // Quick active toggle
    document.querySelectorAll(".toggle-active").forEach(chk => {
      chk.addEventListener("change", async () => {
        const id = chk.dataset.id;
        await fetch(`/api/v1/admin/products/${id}/quick-update`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ is_active: chk.checked })
        });
        refreshStats();
      });
    });

    // Delete product
    document.querySelectorAll(".btn-delete-product").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        if (!confirm(`Are you sure you want to delete product #${id}?`)) return;
        await fetch(`/api/v1/admin/products/${id}`, { method: "DELETE" });
        loadProducts();
        refreshStats();
      });
    });

    // Edit product modal
    document.querySelectorAll(".btn-edit-product").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        openProductEditModal(id);
      });
    });
  }

  // --- PRODUCT CREATE & EDIT MODAL ---
  function setupProductForm() {
    const modal = document.getElementById("product-form-modal");
    const newBtn = document.getElementById("btn-new-product");
    const closeBtn = document.getElementById("btn-close-product-modal");
    const form = document.getElementById("product-form");

    if (newBtn) {
      newBtn.addEventListener("click", () => {
        form.reset();
        document.getElementById("prod-modal-id").value = "";
        document.getElementById("prod-modal-title").textContent = "Add New Handcrafted Product";
        modal.classList.add("active");
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener("click", () => modal.classList.remove("active"));
    }

    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.getElementById("prod-modal-id").value;
        const name = document.getElementById("prod-name").value;
        const sku = document.getElementById("prod-sku").value;
        const price = parseFloat(document.getElementById("prod-price").value);
        const regularPrice = parseFloat(document.getElementById("prod-reg-price").value) || price;
        const catId = document.getElementById("prod-category").value;
        const desc = document.getElementById("prod-desc").value;
        const imgUrl = document.getElementById("prod-image-url").value;

        const payload = {
          name,
          sku,
          price,
          regular_price: regularPrice,
          category_id: catId,
          description: desc,
          short_description: desc.substring(0, 150),
          images: [{ url: imgUrl, is_cover: true, alt: name }],
          variants: [
            { id: "var_std", title: "Standard Finish (Warm White 2700K)", price: price, regular_price: regularPrice, sku: `${sku}-STD` },
            { id: "var_sig", title: "Signature Edition (Soft White 3000K)", price: price * 1.25, regular_price: regularPrice * 1.25, sku: `${sku}-SIG` }
          ],
          metadata: {
            material: "Solid Travertine & Frosted Blown Glass",
            bulb_type: "Integrated Dimmable Warm LED",
            color_temperature: "2700K Warm Ambient",
            voltage: "110-240V Universal Adapter"
          }
        };

        try {
          if (id) {
            await fetch(`/api/v1/admin/products/${id}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
          } else {
            await fetch("/api/v1/admin/products", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
          }
          modal.classList.remove("active");
          loadProducts();
          refreshStats();
        } catch (err) {
          alert("Error saving product: " + err);
        }
      });
    }

    // Filter controls
    const searchInput = document.getElementById("admin-search-products");
    if (searchInput) {
      let deb = null;
      searchInput.addEventListener("input", (e) => {
        clearTimeout(deb);
        deb = setTimeout(() => {
          admin.search = e.target.value.trim();
          admin.page = 1;
          loadProducts();
        }, 250);
      });
    }

    const sourceSelect = document.getElementById("admin-source-filter");
    if (sourceSelect) {
      sourceSelect.addEventListener("change", (e) => {
        admin.sourceFilter = e.target.value;
        admin.page = 1;
        loadProducts();
      });
    }

    document.getElementById("btn-prev-page").addEventListener("click", () => {
      if (admin.page > 1) {
        admin.page--;
        loadProducts();
      }
    });

    document.getElementById("btn-next-page").addEventListener("click", () => {
      if (admin.page < admin.totalPages) {
        admin.page++;
        loadProducts();
      }
    });
  }

  async function openProductEditModal(id) {
    try {
      const resp = await fetch(`/api/v1/catalog/products/${id}`);
      const p = await resp.json();

      document.getElementById("prod-modal-id").value = p.id;
      document.getElementById("prod-name").value = p.name;
      document.getElementById("prod-sku").value = p.sku;
      document.getElementById("prod-price").value = p.price;
      document.getElementById("prod-reg-price").value = p.regular_price || p.price;
      document.getElementById("prod-category").value = p.category_id || "";
      document.getElementById("prod-desc").value = p.description || "";
      document.getElementById("prod-image-url").value = (p.images && p.images[0]) ? p.images[0].url : "";

      document.getElementById("prod-modal-title").textContent = `Edit Product: ${p.name}`;
      document.getElementById("product-form-modal").classList.add("active");
    } catch (e) {
      alert("Failed to load product details: " + e);
    }
  }

  // --- CATEGORIES ---
  async function loadCategories() {
    try {
      const resp = await fetch("/api/v1/admin/categories");
      const cats = await resp.json();
      admin.categories = cats;

      // Populate category selects
      const catSelect = document.getElementById("prod-category");
      if (catSelect) {
        catSelect.innerHTML = `<option value="">Select Category...</option>` +
          cats.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
      }

      const table = document.getElementById("admin-categories-tbody");
      if (table) {
        table.innerHTML = cats.map(c => `
          <tr>
            <td><strong>${c.name}</strong></td>
            <td><code>${c.slug}</code></td>
            <td>${c.product_count} fixtures</td>
            <td>
              <span class="badge" style="background:${c.is_visible ? '#dcfce7' : '#fee2e2'}; color:${c.is_visible ? '#15803d' : '#991b1b'};">
                ${c.is_visible ? 'Visible' : 'Hidden'}
              </span>
            </td>
            <td>
              <button class="btn btn-outline btn-del-cat" data-id="${c.id}" style="min-height:28px; padding:0.2rem 0.5rem; font-size:0.75rem; color:#ef4444;">Delete</button>
            </td>
          </tr>
        `).join("");

        document.querySelectorAll(".btn-del-cat").forEach(btn => {
          btn.addEventListener("click", async () => {
            if (!confirm("Delete this category?")) return;
            await fetch(`/api/v1/admin/categories/${btn.dataset.id}`, { method: "DELETE" });
            loadCategories();
          });
        });
      }
    } catch (e) {
      console.error("Failed to load categories", e);
    }
  }

  function setupCategoryForm() {
    const form = document.getElementById("category-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("cat-name").value;
        const slug = document.getElementById("cat-slug").value || name.toLowerCase().replace(/ /g, "-");
        await fetch("/api/v1/admin/categories", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, slug, is_visible: true })
        });
        form.reset();
        loadCategories();
        refreshStats();
      });
    }
  }

  // --- SYNCHRONIZATION CONTROLS ---
  function setupSyncControls() {
    const btnShopify = document.getElementById("btn-sync-shopify");
    const btnWc = document.getElementById("btn-sync-wc");
    const btnAll = document.getElementById("btn-sync-all");
    const progressBox = document.getElementById("sync-progress-box");
    const progressBar = document.getElementById("sync-progress-bar");
    const progressStatus = document.getElementById("sync-progress-status");

    async function triggerSync(source) {
      progressBox.style.display = "block";
      progressBar.style.width = "30%";
      progressStatus.textContent = `Connecting to ${source.toUpperCase()} endpoint & fetching catalogue...`;

      try {
        let endpoint = `/api/v1/admin/sync/${source}`;
        progressBar.style.width = "65%";
        progressStatus.textContent = `Analyzing diffs, deduplicating SKUs, and synchronizing database...`;

        const resp = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ source })
        });
        const res = await resp.json();

        progressBar.style.width = "100%";
        progressStatus.textContent = `✓ Synchronization completed successfully! Fetched: ${res.items_fetched || res.total_created || 0} items.`;
        
        setTimeout(() => {
          progressBox.style.display = "none";
          progressBar.style.width = "0%";
        }, 3000);

        refreshStats();
        loadProducts();
        loadSyncHistory();
        loadAuditLog();
      } catch (err) {
        progressBar.style.background = "#ef4444";
        progressStatus.textContent = `❌ Sync failed: ${err.message}`;
      }
    }

    if (btnShopify) btnShopify.addEventListener("click", () => triggerSync("shopify"));
    if (btnWc) btnWc.addEventListener("click", () => triggerSync("woocommerce"));
    if (btnAll) btnAll.addEventListener("click", () => triggerSync("all"));
  }

  async function loadSyncHistory() {
    try {
      const resp = await fetch("/api/v1/admin/sync/history?limit=25");
      const logs = await resp.json();
      admin.syncLogs = logs;

      const tbody = document.getElementById("sync-history-tbody");
      if (tbody) {
        tbody.innerHTML = logs.map(l => `
          <tr>
            <td><code>${l.id.substring(0, 8)}</code></td>
            <td><strong>${l.source.toUpperCase()}</strong></td>
            <td>
              <span class="badge" style="background:${l.status === 'success' ? '#dcfce7' : '#fee2e2'}; color:${l.status === 'success' ? '#15803d' : '#991b1b'};">
                ${l.status.toUpperCase()}
              </span>
            </td>
            <td>${l.started_at}</td>
            <td>${l.duration_ms} ms</td>
            <td>${l.items_fetched}</td>
            <td>+${l.items_created} / ~${l.items_updated} / =${l.items_unchanged}</td>
            <td style="color:#ef4444; font-size:0.75rem;">${l.error_message || '-'}</td>
          </tr>
        `).join("");
      }
    } catch (e) {
      console.error("Failed to load sync history", e);
    }
  }

  async function loadAuditLog() {
    try {
      const resp = await fetch("/api/v1/admin/audit-log?limit=50");
      const logs = await resp.json();
      admin.auditLogs = logs;

      const tbody = document.getElementById("audit-log-tbody");
      if (tbody) {
        tbody.innerHTML = logs.map(a => `
          <tr>
            <td><span style="font-size:0.8rem; color:#64748b;">${a.created_at}</span></td>
            <td><strong>${a.product_name}</strong></td>
            <td>
              <span class="badge" style="background:#e0f2fe; color:#0369a1;">${a.action}</span>
            </td>
            <td><code style="font-size:0.75rem;">${a.changes_json}</code></td>
            <td><span class="badge badge-source-manual">${a.actor}</span></td>
          </tr>
        `).join("");
      }
    } catch (e) {
      console.error("Failed to load audit log", e);
    }
  }

  // --- SETTINGS (Active Design, WhatsApp Number, Banner) ---
  async function loadSettings() {
    try {
      const resp = await fetch("/api/v1/admin/settings");
      const s = await resp.json();
      admin.settings = s;

      document.getElementById("setting-store-name").value = s.store_name || "";
      document.getElementById("setting-tagline").value = s.tagline || "";
      document.getElementById("setting-wa-number").value = s.whatsapp_number || "";
      document.getElementById("setting-wa-template").value = s.whatsapp_message_template || "";
      document.getElementById("setting-active-design").value = s.active_design || "rajdhani";
      document.getElementById("setting-banner-text").value = s.banner_announcement || "";
      document.getElementById("setting-banner-active").checked = (s.banner_is_active === "1");
    } catch (e) {
      console.error("Failed to load settings", e);
    }
  }

  function setupSettingsForm() {
    const form = document.getElementById("settings-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
          store_name: document.getElementById("setting-store-name").value,
          tagline: document.getElementById("setting-tagline").value,
          whatsapp_number: document.getElementById("setting-wa-number").value,
          whatsapp_message_template: document.getElementById("setting-wa-template").value,
          active_design: document.getElementById("setting-active-design").value,
          banner_announcement: document.getElementById("setting-banner-text").value,
          banner_is_active: document.getElementById("setting-banner-active").checked
        };

        const res = await fetch("/api/v1/admin/settings", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          const btn = document.getElementById("btn-save-settings");
          btn.textContent = "Saved Successfully!";
          setTimeout(() => btn.textContent = "Save Settings", 2000);
        }
      });
    }
  }

  // --- SOURCE UPDATE SIMULATION (Requirement 19.9) ---
  function setupSimulationTools() {
    const simBtn = document.getElementById("btn-simulate-source-change");
    const simResult = document.getElementById("sim-result-box");

    if (simBtn) {
      simBtn.addEventListener("click", async () => {
        const source = document.getElementById("sim-source").value;
        const newPrice = parseFloat(document.getElementById("sim-price").value) || 188888;
        simBtn.textContent = "Updating External Source...";

        try {
          const res = await fetch("/mock-source/simulate/modify-product", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ source: source, field: "price", new_value: newPrice })
          });
          const data = await res.json();
          simResult.style.display = "block";
          simResult.innerHTML = `
            <div style="background:#fef3c7; border:1px solid #f59e0b; padding:0.75rem; border-radius:6px; font-size:0.85rem; color:#92400e;">
              <strong>External Store Updated:</strong> ${data.message}<br/>
              <em>Next step:</em> Click <strong>"Run Synchronization"</strong> above to pull this change into the local catalog without full overwrite!
            </div>
          `;
          simBtn.textContent = "Update Applied to Source!";
          setTimeout(() => simBtn.textContent = "Simulate External Price Update", 2000);
        } catch (e) {
          alert("Simulation failed: " + e);
          simBtn.textContent = "Simulate External Price Update";
        }
      });
    }
  }

})();
