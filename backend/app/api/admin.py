from fastapi import APIRouter, Depends, HTTPException, Query, Body
import aiosqlite
import json
import uuid
from typing import Optional, List, Dict, Any
from ..database import get_db, get_sync_db
from ..models import (
    ProductCreateUpdate, QuickUpdateProduct, CategoryCreateUpdate,
    SettingsUpdate, SyncTriggerRequest, SyncLogResponse
)
from ..services.diff_engine import compute_product_hash
from ..services.shopify_sync import sync_shopify_catalog
from ..services.woocommerce_sync import sync_woocommerce_catalog

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

# --- STATS & OVERVIEW ---
@router.get("/stats")
async def get_admin_stats(db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns dashboard counts: total products, active products, total categories,
    out of stock products, shopify synced, woocommerce synced, total whatsapp enquiries.
    """
    async with db.execute("SELECT COUNT(*) as count FROM products") as cur:
        total_prods = (await cur.fetchone())["count"]
    async with db.execute("SELECT COUNT(*) as count FROM products WHERE is_active = 1") as cur:
        active_prods = (await cur.fetchone())["count"]
    async with db.execute("SELECT COUNT(*) as count FROM products WHERE stock_status = 'outofstock' OR stock_quantity <= 0") as cur:
        outofstock = (await cur.fetchone())["count"]
    async with db.execute("SELECT COUNT(*) as count FROM products WHERE source = 'shopify'") as cur:
        shopify_prods = (await cur.fetchone())["count"]
    async with db.execute("SELECT COUNT(*) as count FROM products WHERE source = 'woocommerce'") as cur:
        wc_prods = (await cur.fetchone())["count"]
    async with db.execute("SELECT COUNT(*) as count FROM categories") as cur:
        total_cats = (await cur.fetchone())["count"]
    async with db.execute("SELECT COUNT(*) as count FROM analytics_events WHERE event_type LIKE 'whatsapp%'") as cur:
        wa_enquiries = (await cur.fetchone())["count"]
    async with db.execute("SELECT COUNT(*) as count FROM analytics_events WHERE event_type = 'product_view'") as cur:
        prod_views = (await cur.fetchone())["count"]

    # Recent sync status
    async with db.execute("SELECT * FROM sync_logs ORDER BY started_at DESC LIMIT 5") as cur:
        recent_syncs = [dict(row) for row in await cur.fetchall()]

    return {
        "total_products": total_prods,
        "active_products": active_prods,
        "outofstock_products": outofstock,
        "shopify_products": shopify_prods,
        "woocommerce_products": wc_prods,
        "total_categories": total_cats,
        "whatsapp_enquiries": wa_enquiries,
        "product_views": prod_views,
        "recent_syncs": recent_syncs
    }

# --- PRODUCT CRUD ---
@router.get("/products")
async def admin_list_products(
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: aiosqlite.Connection = Depends(get_db)
):
    conditions = []
    params = []

    if search:
        s = f"%{search.strip().lower()}%"
        conditions.append("(LOWER(name) LIKE ? OR LOWER(sku) LIKE ?)")
        params.extend([s, s])
    if category_id:
        conditions.append("category_id = ?")
        params.append(category_id)
    if source:
        conditions.append("source = ?")
        params.append(source)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    async with db.execute(f"SELECT COUNT(*) as count FROM products {where}", params) as cur:
        total = (await cur.fetchone())["count"]

    offset = (page - 1) * page_size
    query = f"""
    SELECT id, source, sku, name, slug, price, regular_price, stock_status,
           stock_quantity, category_name, is_active, is_featured, created_at, updated_at,
           images_json
    FROM products
    {where}
    ORDER BY updated_at DESC
    LIMIT ? OFFSET ?
    """
    async with db.execute(query, params + [page_size, offset]) as cur:
        rows = await cur.fetchall()
        items = []
        for r in rows:
            imgs = json.loads(r["images_json"] or "[]")
            cover = imgs[0]["url"] if imgs else "/static/images/placeholder.svg"
            items.append({
                **dict(r),
                "cover_image": cover
            })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size)
    }

@router.post("/products")
async def admin_create_product(product: ProductCreateUpdate, db: aiosqlite.Connection = Depends(get_db)):
    """
    Manually add a product from the Admin panel.
    """
    prod_id = f"custom_{uuid.uuid4().hex[:8]}"
    slug = product.slug or product.name.lower().replace(" ", "-").replace("&", "and")
    
    # Check category name
    cat_name = ""
    if product.category_id:
        async with db.execute("SELECT name FROM categories WHERE id = ?", (product.category_id,)) as cur:
            row = await cur.fetchone()
            if row:
                cat_name = row["name"]

    prod_dict = product.model_dump()
    prod_dict["category_name"] = cat_name
    content_hash = compute_product_hash(prod_dict)

    images_json = json.dumps(product.images)
    variants_json = json.dumps(product.variants)
    metadata_json = json.dumps(product.metadata)

    try:
        await db.execute("""
            INSERT INTO products (
                id, source, source_id, sku, name, slug, description, short_description,
                price, regular_price, currency, stock_status, stock_quantity,
                category_id, category_name, images_json, variants_json, metadata_json,
                source_url, is_featured, is_active, content_hash, created_at, updated_at
            ) VALUES (?, 'manual', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            prod_id, prod_id, product.sku, product.name, slug, product.description,
            product.short_description, product.price, product.regular_price or product.price,
            product.currency, product.stock_status, product.stock_quantity, product.category_id,
            cat_name, images_json, variants_json, metadata_json, product.source_url or "",
            1 if product.is_featured else 0, 1 if product.is_active else 0, content_hash
        ))

        await db.execute("""
            INSERT INTO product_audit_log (product_id, product_name, action, changes_json, actor)
            VALUES (?, ?, 'created', ?, 'admin')
        """, (prod_id, product.name, json.dumps({"action": "manual_create"})))

        await db.commit()
        return {"success": True, "id": prod_id, "message": "Product created successfully"}
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Duplicate SKU or Slug: {str(e)}")

@router.put("/products/{id}")
async def admin_update_product(id: str, product: ProductCreateUpdate, db: aiosqlite.Connection = Depends(get_db)):
    """
    Edit existing product.
    """
    async with db.execute("SELECT * FROM products WHERE id = ?", (id,)) as cur:
        existing = await cur.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

    cat_name = ""
    if product.category_id:
        async with db.execute("SELECT name FROM categories WHERE id = ?", (product.category_id,)) as cur:
            row = await cur.fetchone()
            if row:
                cat_name = row["name"]

    prod_dict = product.model_dump()
    prod_dict["category_name"] = cat_name
    content_hash = compute_product_hash(prod_dict)

    await db.execute("""
        UPDATE products SET
            name = ?,
            sku = ?,
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
            is_featured = ?,
            is_active = ?,
            content_hash = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        product.name, product.sku, product.description, product.short_description,
        product.price, product.regular_price or product.price, product.stock_status,
        product.stock_quantity, product.category_id, cat_name, json.dumps(product.images),
        json.dumps(product.variants), json.dumps(product.metadata),
        1 if product.is_featured else 0, 1 if product.is_active else 0,
        content_hash, id
    ))

    await db.execute("""
        INSERT INTO product_audit_log (product_id, product_name, action, changes_json, actor)
        VALUES (?, ?, 'updated', ?, 'admin')
    """, (id, product.name, json.dumps({"action": "admin_edit"})))

    await db.commit()
    return {"success": True, "message": "Product updated"}

@router.patch("/products/{id}/quick-update")
async def admin_quick_update_product(id: str, update: QuickUpdateProduct, db: aiosqlite.Connection = Depends(get_db)):
    """
    Quick inline edit for price and stock availability right from the table.
    """
    async with db.execute("SELECT id, name, price, stock_status FROM products WHERE id = ?", (id,)) as cur:
        prod = await cur.fetchone()
        if not prod:
            raise HTTPException(status_code=404, detail="Product not found")

    updates = []
    params = []
    changes = {}

    if update.price is not None:
        updates.append("price = ?")
        params.append(update.price)
        changes["price"] = {"old": prod["price"], "new": update.price}

    if update.regular_price is not None:
        updates.append("regular_price = ?")
        params.append(update.regular_price)

    if update.stock_status is not None:
        updates.append("stock_status = ?")
        params.append(update.stock_status)
        changes["stock_status"] = {"old": prod["stock_status"], "new": update.stock_status}

    if update.stock_quantity is not None:
        updates.append("stock_quantity = ?")
        params.append(update.stock_quantity)

    if update.is_active is not None:
        updates.append("is_active = ?")
        params.append(1 if update.is_active else 0)

    if not updates:
        return {"success": True, "message": "No changes requested"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(id)

    await db.execute(f"UPDATE products SET {', '.join(updates)} WHERE id = ?", params)

    await db.execute("""
        INSERT INTO product_audit_log (product_id, product_name, action, changes_json, actor)
        VALUES (?, ?, 'quick_update', ?, 'admin')
    """, (id, prod["name"], json.dumps(changes)))

    await db.commit()
    return {"success": True, "message": "Quick update applied", "changes": changes}

@router.delete("/products/{id}")
async def admin_delete_product(id: str, db: aiosqlite.Connection = Depends(get_db)):
    """
    Delete a product from the catalog.
    """
    async with db.execute("SELECT name FROM products WHERE id = ?", (id,)) as cur:
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        prod_name = row["name"]

    await db.execute("DELETE FROM products WHERE id = ?", (id,))
    await db.execute("""
        INSERT INTO product_audit_log (product_id, product_name, action, changes_json, actor)
        VALUES (?, ?, 'deleted', '{}', 'admin')
    """, (id, prod_name))
    await db.commit()
    return {"success": True, "message": f"Product '{prod_name}' deleted"}

# --- CATEGORIES ---
@router.get("/categories")
async def admin_list_categories(db: aiosqlite.Connection = Depends(get_db)):
    query = """
    SELECT c.*, COUNT(p.id) as product_count
    FROM categories c
    LEFT JOIN products p ON p.category_id = c.id
    GROUP BY c.id
    ORDER BY c.display_order ASC, c.name ASC
    """
    async with db.execute(query) as cur:
        return [dict(r) for r in await cur.fetchall()]

@router.post("/categories")
async def admin_create_category(category: CategoryCreateUpdate, db: aiosqlite.Connection = Depends(get_db)):
    cat_id = f"cat_{uuid.uuid4().hex[:6]}"
    slug = category.slug or category.name.lower().replace(" ", "-").replace("&", "and")
    await db.execute("""
        INSERT INTO categories (id, slug, name, description, image_url, display_order, is_visible)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        cat_id, slug, category.name, category.description,
        category.image_url, category.display_order, 1 if category.is_visible else 0
    ))
    await db.commit()
    return {"success": True, "id": cat_id, "message": "Category created"}

@router.put("/categories/{id}")
async def admin_update_category(id: str, category: CategoryCreateUpdate, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("""
        UPDATE categories SET
            name = ?,
            slug = ?,
            description = ?,
            image_url = ?,
            display_order = ?,
            is_visible = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        category.name, category.slug, category.description,
        category.image_url, category.display_order,
        1 if category.is_visible else 0, id
    ))
    await db.commit()
    return {"success": True, "message": "Category updated"}

@router.delete("/categories/{id}")
async def admin_delete_category(id: str, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("DELETE FROM categories WHERE id = ?", (id,))
    await db.commit()
    return {"success": True, "message": "Category deleted"}

# --- STORE SETTINGS (Design switch, WhatsApp number, Announcement) ---
@router.get("/settings")
async def get_admin_settings(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT key, value FROM store_settings") as cur:
        rows = await cur.fetchall()
        return {r["key"]: r["value"] for r in rows}

@router.put("/settings")
async def update_admin_settings(settings_data: SettingsUpdate, db: aiosqlite.Connection = Depends(get_db)):
    """
    Updates WhatsApp number, active catalog design, banner announcement, and auto-sync preferences.
    """
    data_dict = settings_data.model_dump(exclude_unset=True)
    for k, v in data_dict.items():
        val_str = str(int(v)) if isinstance(v, bool) else str(v)
        await db.execute("""
            INSERT INTO store_settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
        """, (k, val_str))
    await db.commit()
    return {"success": True, "message": "Settings updated"}

# --- SYNCHRONIZATION CONTROLS ---
@router.post("/sync/shopify")
async def trigger_shopify_sync(req: SyncTriggerRequest = Body(default_factory=SyncTriggerRequest)):
    """
    Trigger manual Shopify import & synchronization.
    """
    result = await sync_shopify_catalog(store_url=req.api_endpoint, api_key=req.api_key, force_full=req.force_full)
    return result

@router.post("/sync/woocommerce")
async def trigger_woocommerce_sync(req: SyncTriggerRequest = Body(default_factory=SyncTriggerRequest)):
    """
    Trigger manual WooCommerce import & synchronization.
    """
    result = await sync_woocommerce_catalog(store_url=req.api_endpoint, consumer_key=req.api_key, consumer_secret=req.api_secret, force_full=req.force_full)
    return result

@router.post("/sync/all")
async def trigger_all_sync(force_full: bool = False):
    """
    Triggers complete catalog synchronization for both Shopify and WooCommerce sources.
    """
    res_shp = await sync_shopify_catalog(force_full=force_full)
    res_wc = await sync_woocommerce_catalog(force_full=force_full)
    return {
        "status": "completed",
        "shopify": res_shp,
        "woocommerce": res_wc,
        "total_created": res_shp.get("items_created", 0) + res_wc.get("items_created", 0),
        "total_updated": res_shp.get("items_updated", 0) + res_wc.get("items_updated", 0),
        "total_unchanged": res_shp.get("items_unchanged", 0) + res_wc.get("items_unchanged", 0)
    }

@router.get("/sync/history")
async def get_sync_history(limit: int = 25, db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns synchronization audit history logs.
    """
    async with db.execute("""
        SELECT * FROM sync_logs ORDER BY started_at DESC LIMIT ?
    """, (limit,)) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

@router.get("/audit-log")
async def get_product_audit_log(limit: int = 50, db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns product change history (Requirement Section 21 & 22).
    """
    async with db.execute("""
        SELECT * FROM product_audit_log ORDER BY created_at DESC LIMIT ?
    """, (limit,)) as cur:
        rows = await cur.fetchall()
        return [dict(r) for r in rows]
