# Catalog Maker: Video Demonstration & Audio Narration Script

**Duration:** ~4–5 minutes  
**Format:** Screen recording with audio voiceover  
**Target:** Evaluators reviewing the Technical Examination Assignment

---

## 🎙️ Video Recording Cue Sheet & Audio Narration

### [0:00 - 0:30] Introduction & Architecture Overview
- **Visual:** Show architecture diagram from README.md or slide, then switch to browser showing the application running at `http://localhost:8000/`.
- **Narration:**
  > *"Hello, and welcome to the technical demonstration of Catalog Maker — a high-speed, mobile-first product catalog platform engineered specifically for frictionless WhatsApp enquiry and conversions. 
  > The core architecture decouples customer browsing from external e-commerce engines: Shopify and WooCommerce products are ingested and synchronized into a high-performance central SQLite database running with Write-Ahead Logging and compound query indexes. The customer frontend consumes our internal Catalog API with sub-10 millisecond response times, zero customer login friction, and two switchable frontend designs. Let's walk through all mandatory features."*

---

### [0:30 - 1:15] Admin Dashboard, Database & Synchronization (Points 1, 5, 6, 7, 8)
- **Visual:** Navigate to `http://localhost:8000/admin`.
- **Narration:**
  > *"First, here is the complete Admin Portal. We can see our key metrics: over 100 products already synced, live WhatsApp enquiry counters, and product view telemetry. 
  > Let's go to the 'Source Sync & Diff' tab. Here we have our dedicated Shopify API connector and WooCommerce API connector. The platform includes over 50 authentic products for Shopify and over 50 for WooCommerce, with full schema fidelity including sizes, knots, weave details, and high-resolution images.
  > When we trigger a synchronization, our differential sync engine calculates SHA-256 content hashes. If no changes occurred, items are detected as unchanged without creating duplicate entries or corrupting existing data. When we view the Product Catalog tab, all 110 items are instantly accessible in our internal database."*

---

### [1:15 - 1:55] Product Management & Pricing/Availability Toggles (Points 2, 3, 4)
- **Visual:** Demonstrate inline price change, stock availability toggle, and category creation.
- **Narration:**
  > *"Administrators have instantaneous control over catalog availability and pricing. In the Product Catalog table, we can change a price inline — let's update this Persian rug from ₹48,000 to ₹45,000 and hit 'Save'. It updates immediately. 
  > We can also flip the stock toggle in one click between 'In Stock' and 'Out of Stock'. 
  > Under the Categories tab, administrators can create new categories, control visibility, and view real-time product counts per category. Every edit is tracked in our persistent Audit Log."*

---

### [1:55 - 2:40] External Source Update Simulation & Diff Detection (Point 9)
- **Visual:** Go to 'Source Sync > Live Demonstration Simulation'. Select Shopify product #81001, enter new price ₹199,999, click 'Apply Change to External Source', then click 'Import / Sync Shopify Catalog', and show the updated price in the catalog and audit log.
- **Narration:**
  > *"Now, let's demonstrate Requirement 19.9: showing an external source update being reflected in the catalog without a full overwrite. 
  > In our live simulation panel, let's pretend the merchant modified the price of Royal Isfahan Silk Carpet on Shopify to ₹199,999. We apply the change to the external store. 
  > Next, we run the Shopify synchronization. Notice the diff engine's output: exactly 1 item updated, 54 unchanged, zero duplicates. When we check our database, product #81001 immediately reflects the new price of ₹199,999, and the exact price diff is recorded in the Audit Log."*

---

### [2:40 - 3:30] Customer Catalog Experience: Browsing, Pop-ups & Lightbox (Points 12, 13, 18)
- **Visual:** Switch to public catalog `http://localhost:8000/`. Hard refresh to show skeleton shimmers, browse category folder pills, click on a carpet to open pop-up, then click image to open lightbox.
- **Narration:**
  > *"Now let's experience the customer catalog. Notice the speed: on initial load, smooth skeleton shimmer cards eliminate layout shifts. When browsing categories like 'Vintage Persian Rugs', 'Moroccan Berber', or 'Kashmir Silk', category switching is instantaneous thanks to our client-side SWR caching.
  > Clicking any carpet card opens a rich modal bottom-sheet in under 50 milliseconds. We see artisan specifications, materials, knot density, and interactive size selectors with dynamic pricing. 
  > Clicking the image launches our touch-friendly full-screen Lightbox with zoom support, arrow keys, and next/previous image navigation."*

---

### [3:30 - 4:15] Wishlist & Multi-Product WhatsApp Enquiry (Points 11, 14, 15, 16)
- **Visual:** Click heart on 2 carpets to show Wishlist. Select 3 carpets using the '+' button. Show the floating bottom WhatsApp dock. Click 'Enquire on WhatsApp' to show the pre-filled message.
- **Narration:**
  > *"Per Section 11 of the specification, there is no cart or checkout — WhatsApp is the primary conversion channel. 
  > First, wishlist functionality works seamlessly with zero login friction. Customers tap the heart icon, and items persist in local storage.
  > Second, customers can select multiple carpets across different collections. As we tap the selection trigger on three different carpets, a sticky WhatsApp enquiry dock slides up showing '3 Carpets Selected'.
  > When we tap 'Enquire on WhatsApp', the system formats the exact pre-filled message specified in the assignment:
  > 'Hi, I am interested in the following products:
  > 1. Royal Isfahan Masterpiece - URL
  > 2. Antique Tabriz Floral - URL
  > 3. Bespoke Royal Jaipur Rug - URL
  > Please share more details and pricing.'
  > It directly opens WhatsApp with the message ready to send."*

---

### [4:15 - 4:55] Multiple Designs & Mobile Responsiveness (Points 10, 11, 17)
- **Visual:** Switch design to 'Nordic Minimalist' via dropdown or Admin settings. Open Chrome DevTools in Mobile device emulation (iPhone / Pixel) and demonstrate touch responsiveness.
- **Narration:**
  > *"Finally, let's showcase Design Versatility and Mobile-First responsiveness. 
  > We support multiple substantially different catalog designs without altering the database or API. With one click, we switch from 'Rajdhani Heritage Carpet Grid' to 'Nordic Minimalist & Editorial Boutique' — transforming the layout into a clean, modern aesthetic with uppercase typography and high-density cards.
  > In mobile view, all touch targets exceed 44 pixels, navigation ribbons scroll smoothly, and bottom sheets provide a native mobile app feel.
  > That completes our demonstration of all 18 mandatory requirements of the High-Speed Product Catalog Platform. Thank you!"*
