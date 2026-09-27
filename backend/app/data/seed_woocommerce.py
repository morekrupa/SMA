"""
WooCommerce Data Source Seed: 55+ Designer Lighting Products formatted in official WooCommerce REST API v3 format:
GET /wp-json/wc/v3/products
"""

import json

WOOCOMMERCE_PRODUCTS = [
    {
        "id": 501,
        "name": "Bespoke Fluted Amber Glass & Walnut Base Table Lamp",
        "slug": "bespoke-fluted-amber-glass-walnut-table-lamp",
        "permalink": "https://woocommerce.luminastudio.local/product/bespoke-fluted-amber-glass-walnut-table-lamp/",
        "date_created": "2024-01-12T10:30:00",
        "date_modified": "2024-02-18T16:45:00",
        "type": "variable",
        "status": "publish",
        "featured": True,
        "catalog_visibility": "visible",
        "description": "<p>A timeless statement lamp crafted from heavy fluted optic amber glass set into a hand-turned American walnut base. Diffuses an inviting, golden hour ambient light across sideboards, consoles, and bedside spaces. Equipped with vintage-style brass toggle switch and braided houndstooth cord.</p>",
        "short_description": "<p>Hand-blown fluted amber glass with FSC-certified solid walnut base.</p>",
        "sku": "WC-LUM-AMB-01",
        "price": "9800",
        "regular_price": "12500",
        "sale_price": "9800",
        "on_sale": True,
        "purchasable": True,
        "total_sales": 24,
        "stock_status": "instock",
        "stock_quantity": 14,
        "categories": [
            {"id": 101, "name": "Luxury Fluted Glass Accent Lamps", "slug": "luxury-fluted-glass-accent-lamps"}
        ],
        "images": [
            {
                "id": 1201,
                "src": "https://images.unsplash.com/photo-1540932239986-30128078f3c5?auto=format&fit=crop&w=1000&q=80",
                "name": "Fluted Amber Glass Lamp Styled",
                "alt": "Bespoke Fluted Amber Glass & Walnut Base Table Lamp"
            },
            {
                "id": 1202,
                "src": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=1000&q=80",
                "name": "Glass optic texture detail",
                "alt": "Fluted amber glass lamp optic refraction"
            }
        ],
        "attributes": [
            {"id": 1, "name": "Size", "options": ["Medium (32cm)", "Grand (42cm)"]},
            {"id": 2, "name": "Glass Tint", "options": ["Amber Gold", "Smoked Quartz"]}
        ],
        "meta_data": [
            {"key": "_artisan_origin", "value": "Murano & Oregon Atelier"},
            {"key": "_material_composition", "value": "Mouth-Blown Optic Glass & Solid Walnut"},
            {"key": "_bulb_spec", "value": "Warm Filament LED 4W E27 (Included)"},
            {"key": "_lumens", "value": "450 Lumens (Warm 2400K Ambient)"}
        ]
    }
]

# Generate 54 additional varied WooCommerce lighting products
WC_CATEGORIES_DATA = [
    {
        "category": "Industrial Edison & Vintage Ambient",
        "cat_slug": "industrial-edison-and-vintage-ambient",
        "names": [
            "Cast Iron Pipe Edison Table Lamp",
            "Steampunk Brass Gauge Cage Lamp",
            "Reclaimed Teak Block Edison Light",
            "Matte Gunmetal Industrial Studio Lamp",
            "Copper Filament Vintage Banker Lamp",
            "Brass Wireframe Geometric Lantern",
            "Heavy Foundry Bronze Desk Light",
            "Vintage Telephone Style Metal Lamp",
            "Warehouse Industrial Spotlight Lamp",
            "Riveted Steel Minimalist Bulb Stand",
            "Antique Boiler Gauge Night Lamp"
        ],
        "material": "Cast Iron, Antiqued Copper & Heavyweight Brass",
        "bulb": "Exposed Spiral Filament Edison Bulb (Included)",
        "lumens": "350 Lumens Warm Amber",
        "base_price": 5400,
        "image_seed": ["photo-1524484485831-a92ffc0de03f", "photo-1507473885765-e6ed057f782c", "photo-1540932239986-30128078f3c5"]
    },
    {
        "category": "Mushroom & Dome Accent Lamps",
        "names": [
            "Retro Ochre Gloss Mushroom Lamp",
            "Panton Style Orange Acrylic Dome Light",
            "Brushed Steel Space Age Table Lamp",
            "Milk Glass Bell Mushroom Night Lamp",
            "Curved Cantilever Metal Dome Lamp",
            "Pastel Mint Italian Mushroom Lamp",
            "Minimalist Chrome Mushroom Table Light",
            "Sunset Yellow Acrylic Glow Lamp",
            "Monochrome Matte Black Mushroom Lamp",
            "Smoked Glass Mushroom Accent Lamp",
            "Coral Pink Mid-Century Dome Light"
        ],
        "material": "Spun Carbon Steel & Hand-Cast Acrylic",
        "bulb": "Dual Omni-Directional Warm LED",
        "lumens": "550 Lumens Glare-Free Ambient",
        "base_price": 6900,
        "image_seed": ["photo-1543198126-a8ad8e47fb22", "photo-1540555700478-4be289fbecef", "photo-1505691938895-1758d7feb511"]
    },
    {
        "category": "Sculptural Marble & Alabaster Lights",
        "names": [
            "Carrara Marble Cylinder Table Light",
            "Nero Marquina Black Marble Cube Lamp",
            "Spanish Alabaster Translucent Glowing Pillar",
            "Verde Guatemala Green Marble Lamp",
            "Travertine Stepped Pedestal Table Lamp",
            "Sculpted Calacatta Gold Marble Light",
            "Onyx Backlit Mineral Crystal Lamp",
            "Raw Edge Limestone Bedside Lamp",
            "Pyramid Alabaster Sacred Glow Light",
            "Monolithic Grey Granite Table Light",
            "Honed Sandstone Ambient Sphere Lamp"
        ],
        "material": "Natural Quarried Italian Marble & Brass Accents",
        "bulb": "Integrated Low-Voltage Concealed LED",
        "lumens": "400 Lumens Soft Subsurface Glow",
        "base_price": 13500,
        "image_seed": ["photo-1517991104123-1d56a6e81ed9", "photo-1507473885765-e6ed057f782c", "photo-1513506003901-1e6a229e2d15"]
    },
    {
        "category": "Bohemian Rattan & Woven Bamboo Lamps",
        "names": [
            "Bali Handwoven Seagrass Table Lamp",
            "Tiered Natural Bamboo Lantern Lamp",
            "Cane Webbing Cylinder Bedside Light",
            "Wicker Dome Coastal Living Accent Lamp",
            "Braided Rattan Gourd Silhouette Lamp",
            "Palm Fiber Tropical Night Lamp",
            "Loomed Jute Drum Shade Table Lamp",
            "Open-Weave Straw Basket Light",
            "Scalloped Bamboo Studio Table Lamp",
            "Sunburst Rattan Halo Table Light",
            "Organic Abaca Fiber Mood Lamp"
        ],
        "material": "Sustainably Harvested Rattan & Natural Bamboo",
        "bulb": "Warm 2200K Decorative Filament LED",
        "lumens": "380 Lumens Pattern-Casting Warmth",
        "base_price": 4800,
        "image_seed": ["photo-1534349762230-e0cadf78f5da", "photo-1540932239986-30128078f3c5", "photo-1517991104123-1d56a6e81ed9"]
    },
    {
        "category": "Modern Touch & Smart Dimmable Lights",
        "names": [
            "Aura Touch Dimmable Ring Light",
            "Eclipse Magnetic Levitation Moon Lamp",
            "Minimalist Touch-Control Bedside Bar",
            "Prism Dichroic Glass Spectrum Lamp",
            "Nebula Ambient Wireless Charging Lamp",
            "Halo Smart RGBW Sunset Table Light",
            "Oasis Acoustic Felt Dimmable Lamp",
            "Arcade Stepless Rotary Brass Lamp",
            "Zenith Balance Floating Light Beam",
            "Chrono Daylight Simulating Desk Lamp"
        ],
        "cat_slug": "modern-touch-and-smart-dimmable-lights",
        "material": "Precision Machined Aircraft Aluminum & Glass",
        "bulb": "Smart Dimmable High CRI 98+ Optical LED",
        "lumens": "800 Lumens (Tunable 2200K - 6500K)",
        "base_price": 8200,
        "image_seed": ["photo-1505691938895-1758d7feb511", "photo-1543198126-a8ad8e47fb22", "photo-1524484485831-a92ffc0de03f"]
    }
]

wc_id = 502
img_id = 1203

for cat_info in WC_CATEGORIES_DATA:
    for name in cat_info["names"]:
        price = cat_info["base_price"] + ((wc_id % 6) * 750)
        reg_price = price + 1500
        slug = name.lower().replace(" ", "-").replace("&", "and").replace("'", "")
        img_hash = cat_info["image_seed"][wc_id % len(cat_info["image_seed"])]
        
        is_instock = (wc_id % 9 != 0)
        stock_status = "instock" if is_instock else "outofstock"
        stock_qty = 8 if is_instock else 0

        prod = {
            "id": wc_id,
            "name": name,
            "slug": slug,
            "permalink": f"https://woocommerce.luminastudio.local/product/{slug}/",
            "date_created": "2024-01-20T11:00:00",
            "date_modified": "2024-02-22T14:30:00",
            "type": "simple",
            "status": "publish",
            "featured": (wc_id % 7 == 0),
            "catalog_visibility": "visible",
            "description": f"<p>Designer lighting fixture: {name}. Meticulously handcrafted from {cat_info['material']}. Comes equipped with {cat_info['bulb']} delivering {cat_info['lumens']}. Creates a calm, luxurious atmosphere with zero glare and superior color fidelity.</p>",
            "short_description": f"<p>{cat_info['material']} with {cat_info['bulb']}.</p>",
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
                {
                    "id": 200 + (wc_id % 5),
                    "name": cat_info["category"],
                    "slug": cat_info.get("cat_slug") or cat_info["category"].lower().replace(" ", "-").replace("&", "and")
                }
            ],
            "images": [
                {
                    "id": img_id,
                    "src": f"https://images.unsplash.com/{img_hash}?auto=format&fit=crop&w=1000&q=80",
                    "name": f"{name} Room View",
                    "alt": f"{name} in luxury bedroom or living room"
                },
                {
                    "id": img_id + 1,
                    "src": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=1000&q=80",
                    "name": f"{name} Surface Detail",
                    "alt": f"{name} lamp shade and hardware detail"
                }
            ],
            "attributes": [
                {"id": 1, "name": "Size", "options": ["Standard Table Height", "Compact Bedside"]},
                {"id": 2, "name": "Lighting Tone", "options": ["Warm Amber 2400K", "Soft White 3000K"]}
            ],
            "meta_data": [
                {"key": "_material_composition", "value": cat_info["material"]},
                {"key": "_bulb_type", "value": cat_info["bulb"]},
                {"key": "_lumens", "value": cat_info["lumens"]},
                {"key": "_certifications", "value": "CE, RoHS, BIS Certified Low-Voltage"}
            ]
        }
        WOOCOMMERCE_PRODUCTS.append(prod)
        wc_id += 1
        img_id += 2

def get_woocommerce_products():
    return WOOCOMMERCE_PRODUCTS
