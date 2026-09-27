import httpx
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from ..database import get_sync_db
from ..services.diff_engine import compute_product_hash, detect_changes
from ..services.image_service import optimize_image_url
from ..config import settings
from ..api.mock_sources import LIVE_WOOCOMMERCE_STORE

logger = logging.getLogger("catalog_maker.woocommerce_sync")

def normalize_woocommerce_product(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms official WooCommerce REST API product object into canonical Catalog Maker product schema.
    """
    price_str = raw.get("price") or raw.get("regular_price") or "0"
    reg_price_str = raw.get("regular_price") or price_str
    try:
        price = float(price_str)
    except (ValueError, TypeError):
        price = 0.0
    try:
        regular_price = float(reg_price_str)
    except (ValueError, TypeError):
        regular_price = price

    sku = raw.get("sku") or f"WC-{raw.get('id')}"
    stock_status = raw.get("stock_status", "instock")
    stock_qty = raw.get("stock_quantity") or (5 if stock_status == "instock" else 0)

    # Categories
    cats = raw.get("categories", [])
    primary_cat = cats[0] if cats else {"name": "Handcrafted Rugs", "slug": "handcrafted-rugs"}
    category_name = primary_cat.get("name", "Handcrafted Rugs")

    # Images
    images_raw = raw.get("images", [])
    images = []
    for idx, img in enumerate(images_raw):
        src = img.get("src", "")
        images.append({
            "url": src,
            "alt": img.get("alt") or img.get("name") or raw.get("name", ""),
            "is_cover": (idx == 0),
            "thumbnail_url": optimize_image_url(src, width=420)
        })

    # Variants / Attributes
    variants = []
    for attr in raw.get("attributes", []):
        if attr.get("name", "").lower() == "size":
            for opt in attr.get("options", []):
                variants.append({
                    "id": f"wc_{raw.get('id')}_{opt.replace(' ', '_')}",
                    "title": f"Size: {opt}",
                    "price": price,
                    "regular_price": regular_price,
                    "sku": f"{sku}-{opt[:3]}",
                    "stock_status": stock_status,
                    "attributes": {"Size": opt}
                })

    # Metadata
    metadata = {}
    for meta in raw.get("meta_data", []):
        key = meta.get("key", "").lstrip("_")
        metadata[key] = meta.get("value")
    metadata["dimensions"] = raw.get("dimensions", {})
    metadata["weight"] = raw.get("weight", "")

    return {
        "source": "woocommerce",
        "source_id": str(raw.get("id")),
        "sku": sku,
        "name": raw.get("name", "Untitled Carpet"),
        "slug": raw.get("slug") or f"wc-{raw.get('id')}",
        "description": raw.get("description", ""),
        "short_description": raw.get("short_description", "") or (raw.get("description", "")[:200] + "..."),
        "price": price,
        "regular_price": regular_price,
        "currency": "INR",
        "stock_status": stock_status,
        "stock_quantity": stock_qty,
        "category_name": category_name,
        "images": images,
        "variants": variants,
        "metadata": metadata,
        "source_url": raw.get("permalink", f"https://woocommerce.local/product/{raw.get('slug')}"),
        "is_featured": 1 if raw.get("featured") else 0,
        "is_active": 1 if raw.get("status") == "publish" else 0
    }

async def fetch_woocommerce_products(store_url: Optional[str] = None, consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches products from remote WooCommerce REST API v3 or uses built-in live mock store.
    """
    if store_url and consumer_key and consumer_secret:
        clean_url = store_url.rstrip("/")
        endpoint = f"{clean_url}/wp-json/wc/v3/products?per_page=100"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(endpoint, auth=(consumer_key, consumer_secret))
            resp.raise_for_status()
            return resp.json()
    else:
        return LIVE_WOOCOMMERCE_STORE

async def sync_woocommerce_catalog(store_url: Optional[str] = None, consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None, force_full: bool = False) -> Dict[str, Any]:
    """
    Synchronizes WooCommerce products into Central SQLite Database.
    Detects diffs, updates prices/descriptions/images, deduplicates, and logs audit events.
    """
    start_time = time.time()
    sync_id = str(uuid.uuid4())

    items_fetched = 0
    items_created = 0
    items_updated = 0
    items_unchanged = 0
    error_message = ""

    with get_sync_db() as conn:
        cursor = conn.cursor()

        # Log sync start
        cursor.execute("""
            INSERT INTO sync_logs (id, source, status, started_at)
            VALUES (?, 'woocommerce', 'running', CURRENT_TIMESTAMP)
        """, (sync_id,))
        conn.commit()

        try:
            raw_products = await fetch_woocommerce_products(store_url, consumer_key, consumer_secret)
            items_fetched = len(raw_products)

            for raw_prod in raw_products:
                norm = normalize_woocommerce_product(raw_prod)

                # Ensure category exists
                cat_slug = norm["category_name"].lower().replace(" ", "-").replace("&", "and")
                cursor.execute("SELECT id FROM categories WHERE slug = ?", (cat_slug,))
                cat_row = cursor.fetchone()
                if cat_row:
                    cat_id = cat_row[0]
                else:
                    cat_id = f"cat_{cat_slug}"
                    cat_img = norm["images"][0]["url"] if norm["images"] else ""
                    cursor.execute("""
                        INSERT INTO categories (id, slug, name, description, image_url, display_order, is_visible)
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                    """, (cat_id, cat_slug, norm["category_name"], f"Artisan collection of {norm['category_name']}", cat_img, 0))

                new_hash = compute_product_hash(norm)

                # Check if product exists by SKU or (source, source_id)
                cursor.execute("""
                    SELECT id, price, regular_price, stock_status, stock_quantity, name, description, 
                           category_name, images_json, content_hash 
                    FROM products 
                    WHERE sku = ? OR (source = 'woocommerce' AND source_id = ?)
                """, (norm["sku"], norm["source_id"]))
                existing = cursor.fetchone()

                images_json_str = json.dumps(norm["images"])
                variants_json_str = json.dumps(norm["variants"])
                metadata_json_str = json.dumps(norm["metadata"])

                if not existing:
                    prod_id = f"wc_{norm['source_id']}"
                    cursor.execute("""
                        INSERT INTO products (
                            id, source, source_id, sku, name, slug, description, short_description,
                            price, regular_price, currency, stock_status, stock_quantity,
                            category_id, category_name, images_json, variants_json, metadata_json,
                            source_url, is_featured, is_active, content_hash, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (
                        prod_id, norm["source"], norm["source_id"], norm["sku"], norm["name"], norm["slug"],
                        norm["description"], norm["short_description"], norm["price"], norm["regular_price"],
                        norm["currency"], norm["stock_status"], norm["stock_quantity"], cat_id, norm["category_name"],
                        images_json_str, variants_json_str, metadata_json_str, norm["source_url"],
                        norm["is_featured"], norm["is_active"], new_hash
                    ))

                    cursor.execute("""
                        INSERT INTO product_audit_log (product_id, product_name, action, changes_json, actor)
                        VALUES (?, ?, 'created', ?, 'sync_woocommerce')
                    """, (prod_id, norm["name"], json.dumps({"source": "woocommerce", "sku": norm["sku"]})))
                    items_created += 1

                else:
                    existing_dict = dict(existing)
                    old_hash = existing_dict.get("content_hash")

                    if old_hash == new_hash and not force_full:
                        items_unchanged += 1
                    else:
                        changes = detect_changes(existing_dict, norm)
                        cursor.execute("""
                            UPDATE products SET
                                name = ?,
                                description = ?,
                                short_description = ?,
                                price = ?,
                                regular_price = ?,
                                stock_status = ?,
                                stock_quantity = ?,
                                category_id = ?,
                                category_name = ?,
                                images_json = ?,
                                variants_json = ?,
                                metadata_json = ?,
                                is_active = ?,
                                content_hash = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (
                            norm["name"], norm["description"], norm["short_description"],
                            norm["price"], norm["regular_price"], norm["stock_status"], norm["stock_quantity"],
                            cat_id, norm["category_name"], images_json_str, variants_json_str,
                            metadata_json_str, norm["is_active"], new_hash, existing_dict["id"]
                        ))

                        cursor.execute("""
                            INSERT INTO product_audit_log (product_id, product_name, action, changes_json, actor)
                            VALUES (?, ?, 'updated', ?, 'sync_woocommerce')
                        """, (existing_dict["id"], norm["name"], json.dumps(changes)))
                        items_updated += 1

            conn.commit()
            duration_ms = int((time.time() - start_time) * 1000)

            cursor.execute("""
                UPDATE sync_logs SET
                    status = 'success',
                    completed_at = CURRENT_TIMESTAMP,
                    duration_ms = ?,
                    items_fetched = ?,
                    items_created = ?,
                    items_updated = ?,
                    items_unchanged = ?,
                    details_json = ?
                WHERE id = ?
            """, (duration_ms, items_fetched, items_created, items_updated, items_unchanged, json.dumps({"source": "woocommerce"}), sync_id))
            conn.commit()

            return {
                "sync_id": sync_id,
                "source": "woocommerce",
                "status": "success",
                "duration_ms": duration_ms,
                "items_fetched": items_fetched,
                "items_created": items_created,
                "items_updated": items_updated,
                "items_unchanged": items_unchanged
            }

        except Exception as e:
            conn.rollback()
            duration_ms = int((time.time() - start_time) * 1000)
            error_message = str(e)
            logger.error(f"WooCommerce sync failed: {error_message}")
            cursor.execute("""
                UPDATE sync_logs SET
                    status = 'failed',
                    completed_at = CURRENT_TIMESTAMP,
                    duration_ms = ?,
                    error_message = ?
                WHERE id = ?
            """, (duration_ms, error_message, sync_id))
            conn.commit()
            return {
                "sync_id": sync_id,
                "source": "woocommerce",
                "status": "failed",
                "error": error_message,
                "duration_ms": duration_ms
            }
