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
from ..api.mock_sources import LIVE_SHOPIFY_STORE

logger = logging.getLogger("catalog_maker.shopify_sync")

def normalize_shopify_product(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms official Shopify REST product object into the canonical Catalog Maker product schema.
    """
    variants = raw.get("variants", [])
    primary_variant = variants[0] if variants else {}
    
    price = float(primary_variant.get("price", 0.0) or 0.0)
    compare_at_price = primary_variant.get("compare_at_price")
    regular_price = float(compare_at_price) if compare_at_price else price
    sku = primary_variant.get("sku") or f"SHP-{raw.get('id')}"
    
    inventory_qty = int(primary_variant.get("inventory_quantity", 1) or 0)
    stock_status = "instock" if inventory_qty > 0 else "outofstock"
    
    images_raw = raw.get("images", [])
    images = []
    for idx, img in enumerate(images_raw):
        src = img.get("src", "")
        images.append({
            "url": src,
            "alt": img.get("alt") or raw.get("title", ""),
            "is_cover": (idx == 0),
            "thumbnail_url": optimize_image_url(src, width=420)
        })
    
    # Normalized variants
    norm_variants = []
    for var in variants:
        norm_variants.append({
            "id": str(var.get("id")),
            "title": var.get("title", "Standard"),
            "price": float(var.get("price", 0.0) or 0.0),
            "regular_price": float(var.get("compare_at_price") or var.get("price") or 0.0),
            "sku": var.get("sku", ""),
            "stock_status": "instock" if (var.get("inventory_quantity", 1) or 0) > 0 else "outofstock",
            "attributes": {"Size": var.get("option1", ""), "Color": var.get("option2", "")}
        })

    # Metadata extraction
    metadata = {}
    for mf in raw.get("metafields", []):
        metadata[mf.get("key")] = mf.get("value")
    if not metadata and raw.get("tags"):
        metadata["tags"] = raw.get("tags")
    metadata["vendor"] = raw.get("vendor", "Rajdhani Artisans")

    category_name = raw.get("product_type") or "Hand-Knotted Silk Carpets"

    return {
        "source": "shopify",
        "source_id": str(raw.get("id")),
        "sku": sku,
        "name": raw.get("title", "Untitled Product"),
        "slug": raw.get("handle") or f"shopify-{raw.get('id')}",
        "description": raw.get("body_html", ""),
        "short_description": (raw.get("body_html", "")[:200] + "...") if raw.get("body_html") else "",
        "price": price,
        "regular_price": regular_price,
        "currency": "INR",
        "stock_status": stock_status,
        "stock_quantity": inventory_qty,
        "category_name": category_name,
        "images": images,
        "variants": norm_variants,
        "metadata": metadata,
        "source_url": f"https://myshopify.com/products/{raw.get('handle')}",
        "is_featured": 1 if "antique" in (raw.get("tags") or "").lower() else 0,
        "is_active": 1 if raw.get("status", "active") == "active" else 0
    }

async def fetch_shopify_products(store_url: Optional[str] = None, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches products from remote Shopify store or uses built-in live mock store.
    """
    if store_url and api_key:
        clean_url = store_url.rstrip("/")
        endpoint = f"{clean_url}/admin/api/2024-01/products.json?limit=250"
        headers = {"X-Shopify-Access-Token": api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(endpoint, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("products", [])
    else:
        # Use live mutable mock store
        return LIVE_SHOPIFY_STORE

async def sync_shopify_catalog(store_url: Optional[str] = None, api_key: Optional[str] = None, force_full: bool = False) -> Dict[str, Any]:
    """
    Synchronizes Shopify products into Central SQLite Database.
    Avoids duplicates, updates changed products, records sync duration and audit log.
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
            VALUES (?, 'shopify', 'running', CURRENT_TIMESTAMP)
        """, (sync_id,))
        conn.commit()

        try:
            raw_products = await fetch_shopify_products(store_url, api_key)
            items_fetched = len(raw_products)

            for raw_prod in raw_products:
                norm = normalize_shopify_product(raw_prod)
                
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
                
                # Calculate deterministic hash
                new_hash = compute_product_hash(norm)
                
                # Check if product exists by SKU or (source, source_id)
                cursor.execute("""
                    SELECT id, price, regular_price, stock_status, stock_quantity, name, description, 
                           category_name, images_json, content_hash 
                    FROM products 
                    WHERE sku = ? OR (source = 'shopify' AND source_id = ?)
                """, (norm["sku"], norm["source_id"]))
                existing = cursor.fetchone()

                images_json_str = json.dumps(norm["images"])
                variants_json_str = json.dumps(norm["variants"])
                metadata_json_str = json.dumps(norm["metadata"])

                if not existing:
                    # Insert new product
                    prod_id = f"shp_{norm['source_id']}"
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
                    
                    # Audit log
                    cursor.execute("""
                        INSERT INTO product_audit_log (product_id, product_name, action, changes_json, actor)
                        VALUES (?, ?, 'created', ?, 'sync_shopify')
                    """, (prod_id, norm["name"], json.dumps({"source": "shopify", "sku": norm["sku"]})))
                    items_created += 1

                else:
                    existing_dict = dict(existing)
                    old_hash = existing_dict.get("content_hash")

                    if old_hash == new_hash and not force_full:
                        items_unchanged += 1
                    else:
                        # Product changed: detect diff
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
                            VALUES (?, ?, 'updated', ?, 'sync_shopify')
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
            """, (duration_ms, items_fetched, items_created, items_updated, items_unchanged, json.dumps({"source": "shopify"}), sync_id))
            conn.commit()

            return {
                "sync_id": sync_id,
                "source": "shopify",
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
            logger.error(f"Shopify sync failed: {error_message}")
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
                "source": "shopify",
                "status": "failed",
                "error": error_message,
                "duration_ms": duration_ms
            }
