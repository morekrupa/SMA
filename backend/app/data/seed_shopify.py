"""
Shopify Data Source Seed: 55+ Lighting & Lamp Products formatted in the official Shopify REST Admin API format:
GET /admin/api/2024-01/products.json
"""

import json

SHOPIFY_PRODUCTS = [
    {
        "id": 81001,
        "title": "Aura Sculptural Travertine & Frosted Glass Table Lamp",
        "body_html": "<p>An architectural centerpiece carved from solid Italian travertine stone paired with a hand-blown frosted opal glass sphere. Emits a soft, ambient glow through an integrated 3-stage touch dimmer (2700K warm ambient light). Designed for serene modern living rooms, executive desks, and bedside sanctuaries.</p>",
        "vendor": "Lumina Studio",
        "product_type": "Sculptural Table Lamps",
        "handle": "aura-sculptural-travertine-table-lamp",
        "created_at": "2024-01-10T08:00:00Z",
        "updated_at": "2024-02-15T12:30:00Z",
        "published_at": "2024-01-11T10:00:00Z",
        "status": "active",
        "tags": "table lamp, travertine, modern, ambient, dimmable, warm led",
        "variants": [
            {
                "id": 91001,
                "product_id": 81001,
                "title": "Natural Roman Travertine / Warm White 2700K",
                "price": "14500.00",
                "regular_price": "18000.00",
                "sku": "LUM-TRAV-01-NAT",
                "inventory_quantity": 8,
                "option1": "Natural Travertine",
                "option2": "2700K Warm"
            },
            {
                "id": 91002,
                "product_id": 81001,
                "title": "Smoked Charcoal Travertine / Warm White 2700K",
                "price": "16500.00",
                "regular_price": "19500.00",
                "sku": "LUM-TRAV-01-SMK",
                "inventory_quantity": 4,
                "option1": "Smoked Charcoal",
                "option2": "2700K Warm"
            }
        ],
        "options": [{"name": "Material Finish"}, {"name": "Color Temperature"}],
        "images": [
            {
                "id": 70001,
                "product_id": 81001,
                "src": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1000&q=80",
                "alt": "Aura Sculptural Travertine Table Lamp styled on wooden credenza",
                "width": 1200,
                "height": 900
            },
            {
                "id": 70002,
                "product_id": 81001,
                "src": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=1000&q=80",
                "alt": "Travertine lamp detail texture and glowing opal sphere",
                "width": 1200,
                "height": 900
            }
        ],
        "metafields": [
            {"key": "material", "value": "Solid Italian Travertine & Frosted Blown Glass"},
            {"key": "bulb_type", "value": "Integrated Warm LED (CRI 95+)"},
            {"key": "color_temperature", "value": "2700K Warm White (3-Step Touch Dimming)"},
            {"key": "dimensions", "value": "Height 34cm x Base Diameter 16cm"},
            {"key": "power_source", "value": "Braided Fabric Cord with USB-C / AC Adapter"}
        ]
    }
]

# Generate 54 additional realistic designer lamps across popular lighting categories
LIGHTING_COLLECTIONS = [
    {
        "category": "Ceramic & Stoneware Table Lamps",
        "names": [
            "Kyoto Ribbed Terracotta Table Lamp",
            "Sienna Textured Ceramic Bedside Lamp",
            "Nordic Oatmeal Glazed Pot Lamp",
            "Moro Archival Raw Clay Table Lamp",
            "Alabaster Vessel Ambient Lamp",
            "Zuma Fluted White Stoneware Lamp",
            "Earthy Olive Matte Ceramic Desk Lamp",
            "Kanso Rounded Wabi-Sabi Clay Lamp",
            "Sand Dune Hand-Thrown Pottery Lamp",
            "Atlas Crater Textured Basalt Lamp",
            "Pebble Contour Ceramic Table Lamp",
            "Tulum Sunbaked Terracotta Night Lamp"
        ],
        "material": "Handcrafted Ceramic Stoneware & Linen Shade",
        "bulb": "E27 Warm Amber LED (Included)",
        "kelvin": "2700K Sunset Warmth",
        "base_price": 7500,
        "image_seed": ["photo-1517991104123-1d56a6e81ed9", "photo-1540932239986-30128078f3c5", "photo-1534349762230-e0cadf78f5da"]
    },
    {
        "category": "Cordless & Portable Accent Lights",
        "names": [
            "Halo Portable Rechargeable Mushroom Lamp",
            "Nomad Touch-Dimming Cordless Lantern",
            "Aero Brushed Brass Battery Table Lamp",
            "Pillar Minimalist Bar & Cafe Cordless Light",
            "Sprout Silicone Touch Bedside Lamp",
            "Lumen Magnetic Base Portable Light",
            "Bistro Amber Glow Cordless Lamp",
            "Orbita Floating Disc Touch Light",
            "Clover Outdoor IP54 Dining Table Lamp",
            "Solace Aluminum Wireless Night Lamp",
            "Glide Minimalist Desk Wand Lamp"
        ],
        "material": "Anodized Aerospace Aluminum & Polycarbonate",
        "bulb": "Lithium-Ion Rechargeable LED (18h Battery)",
        "kelvin": "Stepless 2200K - 3000K Dimming",
        "base_price": 5200,
        "image_seed": ["photo-1543198126-a8ad8e47fb22", "photo-1507473885765-e6ed057f782c", "photo-1540555700478-4be289fbecef"]
    },
    {
        "category": "Mid-Century Brass & Opal Glass",
        "names": [
            "Atelier Spun Brass Twin-Globe Lamp",
            "Gatsby Brushed Gold Art Deco Lamp",
            "Mid-Century Arc Balance Table Lamp",
            "Astral Polished Brass Eclipse Lamp",
            "Equinox Dual Spherical Accent Lamp",
            "Cosmo Brass Stem Floating Orb Lamp",
            "Linear Bauhaus Brass Reading Lamp",
            "Solarium Champagne Brass Desk Lamp",
            "Vintage Milano Tripod Brass Lamp",
            "Aura Saturn Ring Brass Accent Light",
            "Regent Fluted Brass Column Lamp"
        ],
        "material": "Solid Spun Brass & Triple-Coated Opal Glass",
        "bulb": "G9 Dimmable Warm LED Capsules",
        "kelvin": "3000K Soft White (CRI 90)",
        "base_price": 11800,
        "image_seed": ["photo-1513506003901-1e6a229e2d15", "photo-1505691938895-1758d7feb511", "photo-1524484485831-a92ffc0de03f"]
    },
    {
        "category": "Minimalist Japandi Paper & Wood",
        "names": [
            "Akari Inspired Rice Paper Lantern Lamp",
            "Kyoto Natural Ash Wood Table Lamp",
            "Origami Pleated Mulberry Paper Light",
            "Bonsai Sculptural Walnut Desk Lamp",
            "Washi Cloud Lantern Ambient Lamp",
            "Zen Garden Bamboo Slatted Lamp",
            "Sora Oval Japanese Paper Night Lamp",
            "Hinoki Wood Scented Ambient Light",
            "Tatami Geometrical Wood Frame Lamp",
            "Minka Traditional Pleat Lantern"
        ],
        "material": "Handmade Mulberry Washi Paper & Solid Walnut",
        "bulb": "Warm Filament LED (No Blue Light)",
        "kelvin": "2200K Candlelight Glow",
        "base_price": 6800,
        "image_seed": ["photo-1534349762230-e0cadf78f5da", "photo-1517991104123-1d56a6e81ed9", "photo-1540932239986-30128078f3c5"]
    },
    {
        "category": "Architectural Task & Desk Lamps",
        "names": [
            "Studio Counterbalance Cantilever Desk Lamp",
            "Draftsman Matte Black Articulating Lamp",
            "Linear Precision Glare-Free Task Light",
            "Bauhaus Tubular Chrome Desk Lamp",
            "Monolith Anodized Reading Beam Lamp",
            "Kinetic Counterweight Studio Lamp",
            "Architect Clamp-On Rotary Arm Light",
            "Apex Asymmetric Optical Desk Lamp",
            "Verve Minimalist Gooseneck Lamp",
            "Tangent Linear Touch Dimmer Lamp"
        ],
        "material": "Precision Steel, Carbon Alloy & Silicone Joint",
        "bulb": "High-Efficiency Honeycomb Optical LED",
        "kelvin": "Adjustable 3000K - 5000K Study Light",
        "base_price": 8900,
        "image_seed": ["photo-1524484485831-a92ffc0de03f", "photo-1507473885765-e6ed057f782c", "photo-1543198126-a8ad8e47fb22"]
    }
]

idx = 81002
var_idx = 91003
img_idx = 70003

for col in LIGHTING_COLLECTIONS:
    for name in col["names"]:
        price = col["base_price"] + ((idx % 7) * 950)
        reg_price = price + 2200
        slug = name.lower().replace(" ", "-").replace("&", "and").replace("'", "")
        img_hash = col["image_seed"][idx % len(col["image_seed"])]
        
        product = {
            "id": idx,
            "title": name,
            "body_html": f"<p>Artisan lighting craftsmanship: {name}. Masterfully constructed from {col['material']}. Equipped with {col['bulb']} calibrated to {col['kelvin']}. Perfect for elevating nightstands, study consoles, and boutique living room side tables with glare-free ambient warmth.</p>",
            "vendor": "Lumina Studio",
            "product_type": col["category"],
            "handle": slug,
            "created_at": "2024-01-15T09:00:00Z",
            "updated_at": "2024-02-20T14:15:00Z",
            "published_at": "2024-01-16T11:00:00Z",
            "status": "active" if (idx % 11 != 0) else "draft",
            "tags": f"{col['category'].lower()}, designer lamp, ambient lighting, led, {slug}",
            "variants": [
                {
                    "id": var_idx,
                    "product_id": idx,
                    "title": "Standard / Warm 2700K",
                    "price": str(float(price)),
                    "regular_price": str(float(reg_price)),
                    "sku": f"LUM-{slug[:8].upper()}-STD",
                    "inventory_quantity": 12 if (idx % 8 != 0) else 0,
                    "option1": "Standard Finish",
                    "option2": "2700K Warm"
                },
                {
                    "id": var_idx + 1,
                    "product_id": idx,
                    "title": "Signature Edition / 3000K Soft",
                    "price": str(float(price * 1.25)),
                    "regular_price": str(float(reg_price * 1.25)),
                    "sku": f"LUM-{slug[:8].upper()}-SIG",
                    "inventory_quantity": 6,
                    "option1": "Signature Edition",
                    "option2": "3000K Soft"
                }
            ],
            "options": [{"name": "Edition"}, {"name": "Color Temperature"}],
            "images": [
                {
                    "id": img_idx,
                    "product_id": idx,
                    "src": f"https://images.unsplash.com/{img_hash}?auto=format&fit=crop&w=1000&q=80",
                    "alt": f"{name} interior room lighting view",
                    "width": 1200,
                    "height": 900
                },
                {
                    "id": img_idx + 1,
                    "product_id": idx,
                    "src": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1000&q=80",
                    "alt": f"{name} close-up lamp texture and switch",
                    "width": 1200,
                    "height": 900
                }
            ],
            "metafields": [
                {"key": "material", "value": col["material"]},
                {"key": "bulb_type", "value": col["bulb"]},
                {"key": "color_temperature", "value": col["kelvin"]},
                {"key": "voltage", "value": "110-240V Universal Adapter Included"},
                {"key": "switch_type", "value": "Integrated Rotary / Touch Dimmer"}
            ]
        }
        SHOPIFY_PRODUCTS.append(product)
        idx += 1
        var_idx += 2
        img_idx += 2

def get_shopify_products():
    return SHOPIFY_PRODUCTS
