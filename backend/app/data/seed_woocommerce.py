"""
WooCommerce Data Source Seed: 55+ Products formatted in the official WooCommerce REST API v3 format:
GET /wp-json/wc/v3/products
"""

import json

WOOCOMMERCE_PRODUCTS = [
    {
        "id": 501,
        "name": "Bespoke Royal Jaipur Hand-Tufted Wool Rug",
        "slug": "bespoke-royal-jaipur-hand-tufted-wool-rug",
        "permalink": "https://woocommerce.rajdhanicarpets.local/product/bespoke-royal-jaipur-hand-tufted-wool-rug/",
        "date_created": "2024-01-12T10:30:00",
        "date_modified": "2024-02-18T16:45:00",
        "type": "variable",
        "status": "publish",
        "featured": True,
        "catalog_visibility": "visible",
        "description": "<p>A sumptuous high-density hand-tufted rug from Jaipur royal atelier traditions. High-pile New Zealand wool with hand-carved dimensional beveling that catches natural sunlight beautifully across modern living rooms.</p>",
        "short_description": "<p>High-density hand-tufted New Zealand wool with carved botanical textures.</p>",
        "sku": "WC-JPR-TUFT-01",
        "price": "36500",
        "regular_price": "42000",
        "sale_price": "36500",
        "on_sale": True,
        "purchasable": True,
        "total_sales": 18,
        "stock_status": "instock",
        "stock_quantity": 6,
        "categories": [
            {"id": 101, "name": "Hand-Tufted Contemporary Rugs", "slug": "hand-tufted-contemporary-rugs"}
        ],
        "images": [
            {
                "id": 1201,
                "src": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1000&q=80",
                "name": "Jaipur Hand Tufted Living Room",
                "alt": "Bespoke Royal Jaipur Hand-Tufted Wool Rug"
            },
            {
                "id": 1202,
                "src": "https://images.unsplash.com/photo-1558882224-dda166733046?auto=format&fit=crop&w=1000&q=80",
                "name": "Jaipur Hand Tufted Texture",
                "alt": "Jaipur Rug weave texture and pile height"
            }
        ],
        "attributes": [
            {"id": 1, "name": "Size", "options": ["5x8 ft", "8x10 ft", "9x12 ft"]},
            {"id": 2, "name": "Colorway", "options": ["Champagne Gold", "Slate Grey"]}
        ],
        "meta_data": [
            {"key": "_artisan_origin", "value": "Jaipur, Rajasthan"},
            {"key": "_material_composition", "value": "80% New Zealand Wool, 20% Viscose highlights"},
            {"key": "_pile_height", "value": "14 mm Hand-Carved Dual Pile"},
            {"key": "_knot_technique", "value": "Tufted with cotton backing"}
        ]
    }
]

# Generate 54 additional varied WooCommerce products
WC_CATEGORIES_DATA = [
    {
        "category": "Vintage Overdyed & Distressed",
        "cat_slug": "vintage-overdyed-and-distressed",
        "names": [
            "Cobalt Blue Distressed Anatolian Rug",
            "Faded Emerald Antique Medallion Rug",
            "Washed Charcoal Vintage Persian Rug",
            "Muted Saffron Overdyed Wool Runner",
            "Distressed Terracotta Turkish Salon Rug",
            "Antique Washed Rose Damask Rug",
            "Mineral Grey Reclaimed Vintage Carpet",
            "Vintage Teal Patchwork Artisan Carpet",
            "Distressed Sandstone Persian Floor Cloth",
            "Weathered Bronze Botanical Wool Carpet",
            "Washed Olive Garden Heritage Rug"
        ],
        "material": "Aged Hand-Spun Anatolian Wool",
        "pile": "Low-Sheared Distressed (4mm)",
        "origin": "Central Anatolia, Turkey",
        "base_price": 28500,
        "image_seed": ["photo-1600585154340-be6161a56a0c", "photo-1596178065887-1198b6148b2b", "photo-1586023492125-27b2c045efd7"]
    },
    {
        "category": "Organic Jute & Natural Fiber",
        "cat_slug": "organic-jute-and-natural-fiber",
        "names": [
            "Braided Sunburst Golden Jute Rug",
            "Chunky Ribbed Natural Hemp Floor Mat",
            "Herringbone Bleached Jute & Cotton Rug",
            "Hand-Coiled Round Spiral Jute Mat",
            "Geometric Charcoal Border Natural Jute Rug",
            "Bleached Seagrass Coastal Living Rug",
            "Boucle Weave Golden Sisal Area Rug",
            "Hand-Loomed Linen & Hemp Flatweave",
            "Rustic Farmhouse Scalloped Jute Rug",
            "Dhurrie Stripe Organic Jute Runner",
            "Diamond Grid Golden Flax Rug"
        ],
        "material": "100% Biodegradable Raw Jute & Sisal",
        "pile": "Textured Flat-Braid (8mm)",
        "origin": "Bengal & Kerala, India",
        "base_price": 12500,
        "image_seed": ["photo-1507652313519-d4e9174996dd", "photo-1540518614846-7ede433c4ef8", "photo-1513519245088-0e12902e5a38"]
    },
    {
        "category": "Kilim & Flatweave Heritage",
        "cat_slug": "kilim-and-flatweave-heritage",
        "names": [
            "Traditional Malatya Reversible Wool Kilim",
            "Balkan Geometric Slit-Weave Tapestry",
            "Ghazni Hand-Spun Wool Tribal Kilim",
            "Navajo Inspired Arrowhead Flatweave",
            "Moroccan Stripe Hand-Woven Kilim Runner",
            "Shirvan Kilim Symmetrical Geometric Rug",
            "Bessarabian Floral Tapestry Kilim",
            "Antalya Sunbeam Earthy Wool Kilim",
            "Kilim Patchwork Contemporary Floor Accent",
            "Kuba Cloth Inspired Geometric Flatweave",
            "Sumak Embroidered Heavyweight Wool Kilim"
        ],
        "material": "Pure Hand-Carded Organic Wool & Goat Hair",
        "pile": "Reversible Zero-Pile Flatweave",
        "origin": "Anatolia & Caucasus",
        "base_price": 19500,
        "image_seed": ["photo-1538688525198-9b88f6f53126", "photo-1579656381226-5fc0f0100c3b", "photo-1616486338812-3dadae4b4ace"]
    },
    {
        "category": "Architectural Geometric & Modernist",
        "cat_slug": "architectural-geometric-and-modernist",
        "names": [
            "Cubist Monochrome Block Wool Carpet",
            "Archways Curved Mid-Century Floor Rug",
            "Metropolis High-Contrast Grid Rug",
            "Bauhaus Primary Tone Geometric Area Rug",
            "Linear Kinetic Optical Illusion Carpet",
            "Terrazzo Abstract Speckled Tufted Rug",
            "Brutalist Concrete Hue Sculpted Rug",
            "Vortex Circular Radial Pattern Carpet",
            "Origami Fold Dimensional Texture Rug",
            "Spectrum Prismatic Contemporary Floor Rug",
            "Rotterdam Bauhaus Asymmetrical Runner"
        ],
        "material": "Semi-Worsted New Zealand Wool & Bamboo Silk",
        "pile": "Multi-Level Loop & Cut Pile (12mm)",
        "origin": "Bhadohi, India",
        "base_price": 31000,
        "image_seed": ["photo-1558882224-dda166733046", "photo-1586023492125-27b2c045efd7", "photo-1513694203232-719a280e022f"]
    },
    {
        "category": "Luxury Round & Oval Accent Rugs",
        "names": [
            "Celestial Moon Phase Circular Silk Rug",
            "Mandala Sunburst Hand-Knotted Round Carpet",
            "Ivory Pearl Floral Medallion Round Rug",
            "Botanical Lotus Leaf Oval Tufted Rug",
            "Emerald Ring Concentric Circle Area Rug",
            "Golden Hour Radial Ombre Round Carpet",
            "Vintage French Aubusson Round Wool Rug",
            "Cosmic Nebula Abstract Circular Rug",
            "Zen Spiral Contoured Pebble Round Rug",
            "Royal Rosewood Medallion Oval Carpet"
        ],
        "cat_slug": "luxury-round-and-oval-accent-rugs",
        "material": "Worsted Wool with Botanical Silk Accents",
        "pile": "10 mm Hand-Sheared Lustrous Pile",
        "origin": "Kashmir & Mirzapur",
        "base_price": 27000,
        "image_seed": ["photo-1600121848594-d8644e57abab", "photo-1600585154340-be6161a56a0c", "photo-1507652313519-d4e9174996dd"]
    }
]

wc_id = 502
img_id = 1203

for cat_info in WC_CATEGORIES_DATA:
    for name in cat_info["names"]:
        price = cat_info["base_price"] + ((wc_id % 6) * 3800)
        reg_price = price + 4500
        slug = name.lower().replace(" ", "-").replace("&", "and").replace("'", "")
        img_hash = cat_info["image_seed"][wc_id % len(cat_info["image_seed"])]
        
        is_instock = (wc_id % 9 != 0)
        stock_status = "instock" if is_instock else "outofstock"
        stock_qty = 5 if is_instock else 0

        prod = {
            "id": wc_id,
            "name": name,
            "slug": slug,
            "permalink": f"https://woocommerce.rajdhanicarpets.local/product/{slug}/",
            "date_created": "2024-01-20T11:00:00",
            "date_modified": "2024-02-22T14:30:00",
            "type": "simple",
            "status": "publish",
            "featured": (wc_id % 7 == 0),
            "catalog_visibility": "visible",
            "description": f"<p>Artisanal masterpiece: {name}. Meticulously handcrafted from {cat_info['material']}. Features {cat_info['pile']} for enduring luxury, resilience, and tactile richness. Hand-finished edges and authentic artisan stamp.</p>",
            "short_description": f"<p>{cat_info['material']}, {cat_info['pile']} from {cat_info['origin']}.</p>",
            "sku": f"WC-{slug[:8].upper()}-{wc_id}",
            "price": str(price),
            "regular_price": str(reg_price),
            "sale_price": str(price) if (wc_id % 3 == 0) else "",
            "on_sale": (wc_id % 3 == 0),
            "purchasable": True,
            "total_sales": (wc_id % 20),
            "stock_status": stock_status,
            "stock_quantity": stock_qty,
            "categories": [
                {"id": 200 + (wc_id % 5), "name": cat_info["category"], "slug": cat_info["cat_slug"]}
            ],
            "images": [
                {
                    "id": img_id,
                    "src": f"https://images.unsplash.com/{img_hash}?auto=format&fit=crop&w=1000&q=80",
                    "name": f"{name} Room View",
                    "alt": f"{name} in luxury room setting"
                },
                {
                    "id": img_id + 1,
                    "src": f"https://images.unsplash.com/photo-1579656381226-5fc0f0100c3b?auto=format&fit=crop&w=1000&q=80",
                    "name": f"{name} Surface Detail",
                    "alt": f"{name} close up weave"
                }
            ],
            "attributes": [
                {"id": 1, "name": "Size", "options": ["4x6 ft", "6x9 ft", "8x10 ft"]},
                {"id": 2, "name": "Weave Style", "options": [cat_info["pile"]]}
            ],
            "meta_data": [
                {"key": "_artisan_origin", "value": cat_info["origin"]},
                {"key": "_material_composition", "value": cat_info["material"]},
                {"key": "_pile_height", "value": cat_info["pile"]},
                {"key": "_authenticity_certificate", "value": "Included with Artisan Signature"}
            ]
        }
        WOOCOMMERCE_PRODUCTS.append(prod)
        wc_id += 1
        img_id += 2

def get_woocommerce_products():
    return WOOCOMMERCE_PRODUCTS
