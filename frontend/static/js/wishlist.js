/**
 * Catalog Maker - Browser-Side Wishlist Manager
 * Persisted in localStorage without requiring customer login.
 */

class WishlistManager {
  constructor() {
    this.storageKey = "catalog_maker_wishlist_v1";
    this.items = this._load();
  }

  _load() {
    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error("Failed to load wishlist from localStorage", e);
      return [];
    }
  }

  _save() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.items));
      window.dispatchEvent(new CustomEvent("wishlist:updated", { detail: { count: this.items.length, items: this.items } }));
    } catch (e) {
      console.error("Failed to save wishlist", e);
    }
  }

  has(productId) {
    return this.items.some(item => item.id === productId);
  }

  toggle(product) {
    const idx = this.items.findIndex(item => item.id === product.id);
    let added = false;
    if (idx >= 0) {
      this.items.splice(idx, 1);
    } else {
      this.items.push({
        id: product.id,
        sku: product.sku,
        name: product.name,
        slug: product.slug,
        price: product.price,
        cover_image: product.cover_image || (product.images && product.images[0] ? product.images[0].url : ""),
        category_name: product.category_name,
        source_url: product.source_url || `${window.location.origin}/#product=${product.id}`
      });
      added = true;
      if (window.apiClient) {
        window.apiClient.recordAnalytics("wishlist_add", product.id, { name: product.name });
      }
    }
    this._save();
    return added;
  }

  remove(productId) {
    this.items = this.items.filter(item => item.id !== productId);
    this._save();
  }

  getItems() {
    return this.items;
  }

  getCount() {
    return this.items.length;
  }

  clear() {
    this.items = [];
    this._save();
  }
}

window.wishlist = new WishlistManager();
