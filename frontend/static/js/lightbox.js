/**
 * Catalog Maker - High-Performance Touch & Keyboard Image Lightbox
 */

class Lightbox {
  constructor() {
    this.images = [];
    this.currentIndex = 0;
    this.isZoomed = false;
    this.overlay = null;
    this._initDom();
    this._bindEvents();
  }

  _initDom() {
    const el = document.createElement("div");
    el.id = "catalog-lightbox";
    el.className = "lightbox-overlay";
    el.innerHTML = `
      <div class="lightbox-controls">
        <button class="lightbox-btn" id="lb-zoom-btn" title="Toggle Zoom">🔍</button>
        <button class="lightbox-btn" id="lb-close-btn" title="Close (Esc)">✕</button>
      </div>
      <button class="lightbox-nav prev" id="lb-prev-btn" title="Previous Image">❮</button>
      <div class="lightbox-img-wrapper">
        <img class="lightbox-img" id="lb-img" src="" alt="Zoomed Product View" />
      </div>
      <button class="lightbox-nav next" id="lb-next-btn" title="Next Image">❯</button>
    `;
    document.body.appendChild(el);
    this.overlay = el;
    this.imgEl = el.querySelector("#lb-img");
  }

  _bindEvents() {
    const closeBtn = this.overlay.querySelector("#lb-close-btn");
    const prevBtn = this.overlay.querySelector("#lb-prev-btn");
    const nextBtn = this.overlay.querySelector("#lb-next-btn");
    const zoomBtn = this.overlay.querySelector("#lb-zoom-btn");

    closeBtn.addEventListener("click", () => this.close());
    prevBtn.addEventListener("click", (e) => { e.stopPropagation(); this.prev(); });
    nextBtn.addEventListener("click", (e) => { e.stopPropagation(); this.next(); });
    zoomBtn.addEventListener("click", (e) => { e.stopPropagation(); this.toggleZoom(); });

    this.imgEl.addEventListener("click", () => this.toggleZoom());

    this.overlay.addEventListener("click", (e) => {
      if (e.target === this.overlay || e.target.classList.contains("lightbox-img-wrapper")) {
        this.close();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (!this.overlay.classList.contains("active")) return;
      if (e.key === "Escape") this.close();
      if (e.key === "ArrowLeft") this.prev();
      if (e.key === "ArrowRight") this.next();
    });
  }

  open(images, startIndex = 0) {
    if (!images || images.length === 0) return;
    this.images = typeof images[0] === "string" ? images : images.map(img => img.url || img.src || img);
    this.currentIndex = startIndex;
    this.isZoomed = false;
    this._render();
    this.overlay.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  close() {
    this.overlay.classList.remove("active");
    document.body.style.overflow = "";
    this.isZoomed = false;
    this.imgEl.style.transform = "scale(1)";
  }

  prev() {
    if (this.images.length <= 1) return;
    this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
    this._render();
  }

  next() {
    if (this.images.length <= 1) return;
    this.currentIndex = (this.currentIndex + 1) % this.images.length;
    this._render();
  }

  toggleZoom() {
    this.isZoomed = !this.isZoomed;
    this.imgEl.style.transform = this.isZoomed ? "scale(1.8)" : "scale(1)";
    this.imgEl.style.cursor = this.isZoomed ? "zoom-out" : "zoom-in";
  }

  _render() {
    const url = this.images[this.currentIndex];
    // Optimize for full-size lightbox rendering
    const fullUrl = url.includes("images.unsplash.com") ? `${url.split("?")[0]}?auto=format&fit=crop&w=1600&q=85` : url;
    this.imgEl.src = fullUrl;
    this.imgEl.style.transform = "scale(1)";
    this.isZoomed = false;
    this.imgEl.style.cursor = "zoom-in";

    const prevBtn = this.overlay.querySelector("#lb-prev-btn");
    const nextBtn = this.overlay.querySelector("#lb-next-btn");
    if (this.images.length <= 1) {
      prevBtn.style.display = "none";
      nextBtn.style.display = "none";
    } else {
      prevBtn.style.display = "flex";
      nextBtn.style.display = "flex";
    }
  }
}

window.lightbox = new Lightbox();
