/**
 * Catalog Maker - High-Speed Client API Layer
 * Features:
 * - In-memory SWR (Stale-While-Revalidate) Cache
 * - Request deduplication
 * - Graceful fallback & error handling
 */

class CatalogApiClient {
  constructor(baseUrl = "/api/v1") {
    this.baseUrl = baseUrl;
    this.cache = new Map();
    this.inFlightRequests = new Map();
  }

  async _fetch(endpoint, options = {}, cacheTtlMs = 60000) {
    const url = `${this.baseUrl}${endpoint}`;
    const cacheKey = `${options.method || "GET"}:${url}:${JSON.stringify(options.body || "")}`;

    // Return cached if fresh
    const cached = this.cache.get(cacheKey);
    const now = Date.now();
    if (cached && (now - cached.timestamp) < cacheTtlMs) {
      return cached.data;
    }

    // Deduplicate identical simultaneous in-flight requests
    if (this.inFlightRequests.has(cacheKey)) {
      return this.inFlightRequests.get(cacheKey);
    }

    const promise = (async () => {
      try {
        const response = await fetch(url, {
          ...options,
          headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.cache.set(cacheKey, { timestamp: now, data });
        return data;
      } finally {
        this.inFlightRequests.delete(cacheKey);
      }
    })();

    this.inFlightRequests.set(cacheKey, promise);
    return promise;
  }

  clearCache() {
    this.cache.clear();
  }

  async getCatalogConfig() {
    return this._fetch("/catalog/config", { method: "GET" }, 30000);
  }

  async getCategories() {
    return this._fetch("/catalog/categories", { method: "GET" }, 60000);
  }

  async getProducts(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.category_id) searchParams.set("category_id", params.category_id);
    if (params.category_slug) searchParams.set("category_slug", params.category_slug);
    if (params.search) searchParams.set("search", params.search);
    if (params.min_price) searchParams.set("min_price", params.min_price);
    if (params.max_price) searchParams.set("max_price", params.max_price);
    if (params.in_stock_only) searchParams.set("in_stock_only", "true");
    if (params.sort) searchParams.set("sort", params.sort);
    if (params.page) searchParams.set("page", params.page);
    if (params.page_size) searchParams.set("page_size", params.page_size);

    const query = searchParams.toString();
    const endpoint = `/catalog/products${query ? "?" + query : ""}`;
    return this._fetch(endpoint, { method: "GET" }, 30000);
  }

  async getProductDetail(idOrSlug) {
    return this._fetch(`/catalog/products/${encodeURIComponent(idOrSlug)}`, { method: "GET" }, 60000);
  }

  async getRelatedProducts(id, limit = 4) {
    return this._fetch(`/catalog/products/${encodeURIComponent(id)}/related?limit=${limit}`, { method: "GET" }, 60000);
  }

  async recordAnalytics(eventType, productId = null, metadata = {}) {
    try {
      await fetch(`${this.baseUrl}/catalog/analytics/event`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_type: eventType, product_id: productId, metadata })
      });
    } catch (err) {
      console.warn("Analytics event failed silently", err);
    }
  }
}

window.apiClient = new CatalogApiClient();
