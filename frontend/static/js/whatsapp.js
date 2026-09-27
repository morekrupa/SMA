/**
 * Catalog Maker - WhatsApp Enquiry Generator & Multi-Select Engine
 * Complies directly with Technical Examination Section 11:
 * "There will be no cart or checkout. WhatsApp is the primary customer conversion mechanism.
 * Customers should be able to select multiple products and generate a pre-filled WhatsApp message."
 */

class WhatsAppEnquiryManager {
  constructor() {
    this.selected = new Map(); // id -> product object
    this.whatsappNumber = "+919876543210";
    this.template = "Hi, I am interested in the following products:\n{product_list}\nPlease share more details and pricing.";
  }

  setWhatsAppNumber(number) {
    if (number) this.whatsappNumber = number;
  }

  setTemplate(tpl) {
    if (tpl) this.template = tpl;
  }

  toggleSelect(product) {
    if (this.selected.has(product.id)) {
      this.selected.delete(product.id);
    } else {
      const prodUrl = `${window.location.origin}/#product=${product.id}`;
      this.selected.set(product.id, {
        id: product.id,
        name: product.name,
        sku: product.sku,
        price: product.price,
        cover_image: product.cover_image || (product.images && product.images[0] ? product.images[0].url : ""),
        url: product.source_url || prodUrl
      });
    }
    this._renderDock();
    window.dispatchEvent(new CustomEvent("selection:updated", {
      detail: { count: this.selected.size, items: Array.from(this.selected.values()) }
    }));
  }

  isSelected(productId) {
    return this.selected.has(productId);
  }

  clearSelection() {
    this.selected.clear();
    this._renderDock();
    window.dispatchEvent(new CustomEvent("selection:updated", {
      detail: { count: 0, items: [] }
    }));
  }

  formatMultiProductMessage(productsList) {
    const list = productsList || Array.from(this.selected.values());
    if (list.length === 0) return "";

    let lines = [];
    list.forEach((p, idx) => {
      const url = p.url || `${window.location.origin}/#product=${p.id}`;
      lines.push(`${idx + 1}. ${p.name} - ${url}`);
    });

    const productListText = lines.join("\n");
    return this.template.replace("{product_list}", productListText);
  }

  formatSingleProductMessage(product) {
    const url = product.source_url || `${window.location.origin}/#product=${product.id}`;
    return `Hi, I am interested in: ${product.name} (SKU: ${product.sku}, Price: ₹${product.price.toLocaleString("en-IN")}) - ${url}\nPlease share availability and delivery details.`;
  }

  sendWhatsAppMessage(messageText) {
    if (window.apiClient) {
      window.apiClient.recordAnalytics("whatsapp_enquiry", null, {
        item_count: this.selected.size,
        message_preview: messageText.substring(0, 100)
      });
    }

    const cleanNumber = this.whatsappNumber.replace(/[^0-9]/g, "");
    const encoded = encodeURIComponent(messageText);
    const waUrl = `https://wa.me/${cleanNumber}?text=${encoded}`;
    window.open(waUrl, "_blank", "noopener,noreferrer");
  }

  sendSingleEnquiry(product) {
    const msg = this.formatSingleProductMessage(product);
    if (window.apiClient) {
      window.apiClient.recordAnalytics("whatsapp_single", product.id, { name: product.name });
    }
    const cleanNumber = this.whatsappNumber.replace(/[^0-9]/g, "");
    const waUrl = `https://wa.me/${cleanNumber}?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, "_blank", "noopener,noreferrer");
  }

  sendMultiEnquiry() {
    if (this.selected.size === 0) {
      alert("Please select at least one carpet to enquire.");
      return;
    }
    const msg = this.formatMultiProductMessage();
    this.sendWhatsAppMessage(msg);
  }

  sendWishlistEnquiry(wishlistItems) {
    if (!wishlistItems || wishlistItems.length === 0) {
      alert("Your wishlist is empty.");
      return;
    }
    const msg = this.formatMultiProductMessage(wishlistItems);
    this.sendWhatsAppMessage(msg);
  }

  _renderDock() {
    let dock = document.getElementById("wa-dock");
    if (!dock) return;

    const count = this.selected.size;
    if (count > 0) {
      dock.classList.add("active");
      const badge = dock.querySelector(".wa-badge");
      const title = dock.querySelector(".wa-dock-title");
      if (badge) badge.textContent = `${count}`;
      if (title) title.textContent = `${count} Carpet${count > 1 ? "s" : ""} Selected for Enquiry`;
    } else {
      dock.classList.remove("active");
    }
  }
}

window.whatsappManager = new WhatsAppEnquiryManager();
