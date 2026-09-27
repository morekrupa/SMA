"""
Shopify Data Source Seed: 55+ Products formatted in the official Shopify REST Admin API format:
GET /admin/api/2024-01/products.json
"""

import json

SHOPIFY_PRODUCTS = [
    {
        "id": 81001,
        "title": "Royal Isfahan Masterpiece Pure Silk Carpet",
        "body_html": "<p>A museum-grade hand-knotted pure mulberry silk carpet woven by master artisans in Isfahan. Features an intricate central medallion surrounded by arabesque floral motifs on an ivory and imperial crimson ground with 900+ KPSI (knots per square inch).</p>",
        "vendor": "Rajdhani Artisans",
        "product_type": "Hand-Knotted Silk Carpets",
        "handle": "royal-isfahan-masterpiece-pure-silk-carpet",
        "created_at": "2024-01-10T08:00:00Z",
        "updated_at": "2024-02-15T12:30:00Z",
        "published_at": "2024-01-11T10:00:00Z",
        "status": "active",
        "tags": "silk, isfahan, antique, luxury, medallion, hand-knotted",
        "variants": [
            {
                "id": 91001,
                "product_id": 81001,
                "title": "5 x 8 ft / Crimson Red",
                "price": "145000.00",
                "regular_price": "165000.00",
                "sku": "SHP-ISF-01-5X8",
                "inventory_quantity": 3,
                "option1": "5 x 8 ft",
                "option2": "Crimson Red"
            },
            {
                "id": 91002,
                "product_id": 81001,
                "title": "8 x 10 ft / Crimson Red",
                "price": "240000.00",
                "regular_price": "270000.00",
                "sku": "SHP-ISF-01-8X10",
                "inventory_quantity": 2,
                "option1": "8 x 10 ft",
                "option2": "Crimson Red"
            }
        ],
        "options": [{"name": "Size"}, {"name": "Color"}],
        "images": [
            {
                "id": 70001,
                "product_id": 81001,
                "src": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?auto=format&fit=crop&w=1000&q=80",
                "alt": "Royal Isfahan Masterpiece Pure Silk Carpet living room view",
                "width": 1200,
                "height": 800
            },
            {
                "id": 70002,
                "product_id": 81001,
                "src": "https://images.unsplash.com/photo-1579656381226-5fc0f0100c3b?auto=format&fit=crop&w=1000&q=80",
                "alt": "Detail weave of Royal Isfahan Silk Carpet",
                "width": 1200,
                "height": 800
            }
        ],
        "metafields": [
            {"key": "material", "value": "100% Pure Mulberry Silk on Silk Warp"},
            {"key": "knot_count", "value": "900 Knots Per Square Inch"},
            {"key": "origin", "value": "Isfahan, Persia"},
            {"key": "pile_height", "value": "6 mm (Low Dense Pile)"}
        ]
    }
]

# Generate 54 additional realistic, varied carpet items to reach 55 Shopify products total
CARPET_COLLECTIONS = [
    {
        "category": "Vintage Persian Rugs",
        "names": [
            "Antique Tabriz Floral Medallion Rug",
            "Kashan Heritage Indigo Wool Rug",
            "Nain Celestial Sky Blue Carpet",
            "Qum Tree of Life Fine Weave",
            "Heriz Geometric Tribal Village Rug",
            "Bijar Iron Rug Ultra-Durable",
            "Shiraz Nomadic Diamond Runner",
            "Kerman Classic Rose Garland Rug",
            "Sarouk Wine Red Luster Rug",
            "Bakhtiari Garden Panel Carpet",
            "Malayer Botanical Medallion Rug",
            "Senneh Fine Tapestry Flatweave"
        ],
        "material": "Highland Virgin Wool on Cotton Foundation",
        "knots": "450-600 KPSI",
        "origin": "Persia / Iran",
        "base_price": 48000,
        "image_seed": ["photo-1596178065887-1198b6148b2b", "photo-1600585154340-be6161a56a0c", "photo-1616486338812-3dadae4b4ace"]
    },
    {
        "category": "Modern Minimalist Rugs",
        "names": [
            "Nordic Linear Ivory Textured Area Rug",
            "Aura Abstract Gradient Cloud Rug",
            "Scandi Ribbed Neutral Wool Carpet",
            "Kyoto Zen Sand Wavy Hand-Tufted Rug",
            "Solstice Organic Pebble Wool Loop Rug",
            "Minimalist Bauhaus Bauhaus Grid Carpet",
            "Alabaster Serenity Plush Rug",
            "Dune Warm Oat Minimalist Rug",
            "Linear Mirage Charcoal Stripe Rug",
            "Echo Neutral Hand-Spun Wool Rug",
            "Copenhagen Dual-Tone Border Rug"
        ],
        "material": "New Zealand Wool & Natural Flax Linen",
        "knots": "Hand-Tufted / 300 KPSI",
        "origin": "Jaipur, India",
        "base_price": 24000,
        "image_seed": ["photo-1558882224-dda166733046", "photo-1513694203232-719a280e022f", "photo-1586023492125-27b2c045efd7"]
    },
    {
        "category": "Moroccan Berber & Tribal",
        "names": [
            "Beni Ourain High-Pile Diamond Shag",
            "Atlas Mountains Geometric Ochre Rug",
            "Azilal Colorful Tribal Story Rug",
            "Boujad Earthy Terracotta Wool Rug",
            "Berber Zigzag High-Density Shag",
            "Tazenakht Sun-Dyed Saffron Rug",
            "High Atlas Monochromatic Tribal Rug",
            "Zanafi Monochrome Flatweave Kilim",
            "Marrakech Medina Textured Wool Rug",
            "Sahara Nomadic Star Pattern Rug",
            "Ouarzazate Sunset Toned Carpet"
        ],
        "material": "100% Unbleached High-Mountain Sheep Wool",
        "knots": "Plush Berber Shag Weave (25mm Pile)",
        "origin": "Middle Atlas, Morocco",
        "base_price": 32000,
        "image_seed": ["photo-1507652313519-d4e9174996dd", "photo-1538688525198-9b88f6f53126", "photo-1540518614846-7ede433c4ef8"]
    },
    {
        "category": "Traditional Kashmir Silk",
        "names": [
            "Srinagar Chinar Leaf Mulberry Silk Carpet",
            "Kashmir Royal Peacock Medallion Rug",
            "Gulmarg Spring Blossom Silk Tapestry",
            "Pahalgam Mughal Hunting Scene Silk Rug",
            "Dal Lake Shimmer Ivory Silk Carpet",
            "Shalimar Floral Garland Silk Carpet",
            "Pashmina Blend Royal Crimson Runner",
            "Kashmiri Golden Amber Silk Rug",
            "Hazratbal Antique Ivory Silk Carpet",
            "Sonamarg Meadow Turquoise Silk Rug"
        ],
        "material": "100% Kashmir Mulberry Silk on Cotton",
        "knots": "750-900 KPSI",
        "origin": "Kashmir, India",
        "base_price": 85000,
        "image_seed": ["photo-1600121848594-d8644e57abab", "photo-1579656381226-5fc0f0100c3b", "photo-1513519245088-0e12902e5a38"]
    },
    {
        "category": "Bohemian Runners & Hallways",
        "names": [
            "Anatolian Sunburst Long Hallway Runner",
            "Vintage Oushak Pastel Rose Runner",
            "Rustic Jute & Wool Braided Corridor Runner",
            "Kazak Bold Medallion Geometric Runner",
            "Tribal Diamond Motif Stair Runner",
            "Herat Indigo Passage Wool Runner",
            "Khotan Pomegranate Silk Runner",
            "Caucasus Eagle Motif Heritage Runner",
            "Persian Afshar Village Wool Runner",
            "Shirvan Stars Symmetrical Runner"
        ],
        "material": "Hand-Spun Ghazni Wool & Hemp",
        "knots": "400 KPSI Flat-Weave Hybrid",
        "origin": "Anatolia & Bhadohi",
        "base_price": 18500,
        "image_seed": ["photo-1596178065887-1198b6148b2b", "photo-1600585154340-be6161a56a0c", "photo-1558882224-dda166733046"]
    }
]

idx = 81002
var_idx = 91003
img_idx = 70003

for col in CARPET_COLLECTIONS:
    for name in col["names"]:
        price = col["base_price"] + ((idx % 7) * 4500)
        reg_price = price + 5000
        slug = name.lower().replace(" ", "-").replace("&", "and").replace("'", "")
        img_hash = col["image_seed"][idx % len(col["image_seed"])]
        
        product = {
            "id": idx,
            "title": name,
            "body_html": f"<p>Exquisite artisan craftsmanship: {name}. Masterfully crafted using {col['material']} with {col['knots']}. Designed to elevate upscale residential interiors and architectural spaces with authentic heritage charm and luxurious underfoot feel.</p>",
            "vendor": "Rajdhani Artisans",
            "product_type": col["category"],
            "handle": slug,
            "created_at": "2024-01-15T09:00:00Z",
            "updated_at": "2024-02-20T14:15:00Z",
            "published_at": "2024-01-16T11:00:00Z",
            "status": "active" if (idx % 11 != 0) else "draft",
            "tags": f"{col['category'].lower()}, hand-made, artisan, luxury, {slug}",
            "variants": [
                {
                    "id": var_idx,
                    "product_id": idx,
                    "title": "5 x 8 ft / Standard",
                    "price": str(float(price)),
                    "regular_price": str(float(reg_price)),
                    "sku": f"SHP-{slug[:8].upper()}-5X8",
                    "inventory_quantity": 4 if (idx % 8 != 0) else 0,
                    "option1": "5 x 8 ft"
                },
                {
                    "id": var_idx + 1,
                    "product_id": idx,
                    "title": "8 x 10 ft / Large",
                    "price": str(float(price * 1.65)),
                    "regular_price": str(float(reg_price * 1.65)),
                    "sku": f"SHP-{slug[:8].upper()}-8X10",
                    "inventory_quantity": 2,
                    "option1": "8 x 10 ft"
                },
                {
                    "id": var_idx + 2,
                    "product_id": idx,
                    "title": "9 x 12 ft / Grand Room",
                    "price": str(float(price * 2.3)),
                    "regular_price": str(float(reg_price * 2.3)),
                    "sku": f"SHP-{slug[:8].upper()}-9X12",
                    "inventory_quantity": 1,
                    "option1": "9 x 12 ft"
                }
            ],
            "options": [{"name": "Size"}],
            "images": [
                {
                    "id": img_idx,
                    "product_id": idx,
                    "src": f"https://images.unsplash.com/{img_hash}?auto=format&fit=crop&w=1000&q=80",
                    "alt": f"{name} primary view",
                    "width": 1200,
                    "height": 900
                },
                {
                    "id": img_idx + 1,
                    "product_id": idx,
                    "src": f"https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1000&q=80",
                    "alt": f"{name} macro knot texture",
                    "width": 1200,
                    "height": 900
                }
            ],
            "metafields": [
                {"key": "material", "value": col["material"]},
                {"key": "knot_count", "value": col["knots"]},
                {"key": "origin", "value": col["origin"]},
                {"key": "pile_height", "value": "8-12 mm"}
            ]
        }
        SHOPIFY_PRODUCTS.append(product)
        idx += 1
        var_idx += 3
        img_idx += 2

def get_shopify_products():
    return SHOPIFY_PRODUCTS
