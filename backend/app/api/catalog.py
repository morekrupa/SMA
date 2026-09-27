from fastapi import APIRouter, Depends, Query, HTTPException, Response
import aiosqlite
import json
from typing import Optional, List, Dict, Any
from ..database import get_db
from ..models import (
    ProductSummary, ProductDetail, ProductImage, ProductVariant,
    CategoryResponse, CatalogConfig, PaginatedProductsResponse, AnalyticsEventCreate
)
from ..services.image_service import optimize_image_url

router = APIRouter(prefix="/catalog", tags=["Internal Fast Catalog API"])

@router.get("/config", response_model=CatalogConfig)
async def get_catalog_config(response: Response, db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns store branding, active design, WhatsApp number, and banner details.
    Cached with ETag & Cache-Control for ultra-fast customer loads.
    """
    response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=300"
    
    async with db.execute("SELECT key, value FROM store_settings") as cursor:
        rows = await cursor.fetchall()
        settings_map = {row["key"]: row["value"] for row in rows}

    async with db.execute("SELECT COUNT(*) as count FROM products WHERE is_active = 1") as cursor:
        row = await cursor.fetchone()
        total_products = row["count"] if row else 0

    async with db.execute("SELECT COUNT(*) as count FROM categories WHERE is_visible = 1") as cursor:
        row = await cursor.fetchone()
        total_categories = row["count"] if row else 0

    return CatalogConfig(
        store_name=settings_map.get("store_name", "Rajdhani Artisans & Digital Carpets"),
        tagline=settings_map.get("tagline", "Handcrafted Luxury Carpets & Rugs"),
        whatsapp_number=settings_map.get("whatsapp_number", "+919876543210"),
        whatsapp_message_template=settings_map.get(
            "whatsapp_message_template", 
            "Hi, I am interested in the following products:\n{product_list}\nPlease share more details and pricing."
        ),
        active_design=settings_map.get("active_design", "rajdhani"),
        currency=settings_map.get("currency", "INR"),
        currency_symbol=settings_map.get("currency_symbol", "₹"),
        banner_announcement=settings_map.get("banner_announcement", "✨ Exclusive Hand-Knotted Silk & Wool Rugs Collection"),
        banner_is_active=(settings_map.get("banner_is_active", "1") == "1"),
        total_products=total_products,
        total_categories=total_categories
    )

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(response: Response, db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns all visible categories with product counts.
    """
    response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=300"
    
    query = """
    SELECT c.id, c.slug, c.name, c.description, c.image_url, c.display_order, c.is_visible,
           COUNT(p.id) as product_count
    FROM categories c
    LEFT JOIN products p ON p.category_id = c.id AND p.is_active = 1
    WHERE c.is_visible = 1
    GROUP BY c.id
    ORDER BY c.display_order ASC, c.name ASC
    """
    async with db.execute(query) as cursor:
        rows = await cursor.fetchall()
        return [
            CategoryResponse(
                id=row["id"],
                slug=row["slug"],
                name=row["name"],
                description=row["description"],
                image_url=row["image_url"],
                display_order=row["display_order"],
                is_visible=bool(row["is_visible"]),
                product_count=row["product_count"]
            )
            for row in rows
        ]

@router.get("/products", response_model=PaginatedProductsResponse)
async def list_products(
    response: Response,
    category_id: Optional[str] = None,
    category_slug: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: Optional[bool] = None,
    sort: Optional[str] = Query("featured", regex="^(featured|price_asc|price_desc|newest|name_asc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    High-performance product listing supporting fast category filtering, search, and sorting.
    Minimal summary payload designed for mobile speed.
    """
    response.headers["Cache-Control"] = "public, max-age=30, stale-while-revalidate=120"
    
    conditions = ["p.is_active = 1"]
    params = []

    if category_id:
        conditions.append("p.category_id = ?")
        params.append(category_id)
    elif category_slug:
        conditions.append("c.slug = ?")
        params.append(category_slug)

    if search:
        search_term = f"%{search.strip().lower()}%"
        conditions.append("(LOWER(p.name) LIKE ? OR LOWER(p.description) LIKE ? OR LOWER(p.sku) LIKE ? OR LOWER(p.category_name) LIKE ?)")
        params.extend([search_term, search_term, search_term, search_term])

    if min_price is not None:
        conditions.append("p.price >= ?")
        params.append(min_price)

    if max_price is not None:
        conditions.append("p.price <= ?")
        params.append(max_price)

    if in_stock_only:
        conditions.append("p.stock_status = 'instock'")

    where_clause = " AND ".join(conditions)

    # Order by clause
    order_map = {
        "featured": "p.is_featured DESC, p.created_at DESC",
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "newest": "p.created_at DESC",
        "name_asc": "p.name ASC"
    }
    order_clause = order_map.get(sort, "p.is_featured DESC, p.created_at DESC")

    # Count total
    count_sql = f"""
    SELECT COUNT(*) as count 
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.id
    WHERE {where_clause}
    """
    async with db.execute(count_sql, params) as cursor:
        row = await cursor.fetchone()
        total = row["count"] if row else 0

    total_pages = max(1, (total + page_size - 1) // page_size)
    offset = (page - 1) * page_size

    # Fetch items
    fetch_sql = f"""
    SELECT p.id, p.sku, p.name, p.slug, p.short_description, p.price, p.regular_price,
           p.currency, p.stock_status, p.category_id, p.category_name, p.images_json,
           p.variants_json, p.metadata_json, p.source, p.source_url, p.is_featured
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.id
    WHERE {where_clause}
    ORDER BY {order_clause}
    LIMIT ? OFFSET ?
    """
    fetch_params = params + [page_size, offset]

    items = []
    async with db.execute(fetch_sql, fetch_params) as cursor:
        rows = await cursor.fetchall()
        for r in rows:
            images = json.loads(r["images_json"] or "[]")
            variants = json.loads(r["variants_json"] or "[]")
            metadata = json.loads(r["metadata_json"] or "{}")

            cover_img = images[0]["url"] if images else "/static/images/placeholder.svg"
            thumbnail = images[0].get("thumbnail_url") if images else "/static/images/placeholder.svg"
            if not thumbnail:
                thumbnail = optimize_image_url(cover_img, width=420)

            variants_summary = [v.get("title", "") for v in variants[:3]]

            items.append(ProductSummary(
                id=r["id"],
                sku=r["sku"],
                name=r["name"],
                slug=r["slug"],
                short_description=r["short_description"] or "",
                price=r["price"],
                regular_price=r["regular_price"],
                currency=r["currency"],
                stock_status=r["stock_status"],
                category_id=r["category_id"],
                category_name=r["category_name"] or "",
                cover_image=cover_img,
                thumbnail_url=thumbnail,
                image_count=len(images),
                variants_summary=variants_summary,
                origin=metadata.get("origin") or metadata.get("artisan_origin", ""),
                material=metadata.get("material") or metadata.get("material_composition", ""),
                source=r["source"],
                source_url=r["source_url"] or "",
                is_featured=bool(r["is_featured"])
            ))

    return PaginatedProductsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=(page < total_pages),
        has_prev=(page > 1)
    )

@router.get("/products/{id_or_slug}", response_model=ProductDetail)
async def get_product_detail(id_or_slug: str, db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns full product details, variants, specs, and gallery images.
    """
    query = """
    SELECT id, source, source_id, sku, name, slug, description, short_description,
           price, regular_price, currency, stock_status, stock_quantity,
           category_id, category_name, images_json, variants_json, metadata_json,
           source_url, is_featured, is_active, created_at, updated_at
    FROM products
    WHERE (id = ? OR slug = ?) AND is_active = 1
    """
    async with db.execute(query, (id_or_slug, id_or_slug)) as cursor:
        r = await cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="Product not found")

        images_raw = json.loads(r["images_json"] or "[]")
        images = []
        for img in images_raw:
            url = img.get("url") if isinstance(img, dict) else str(img)
            alt = img.get("alt", r["name"]) if isinstance(img, dict) else r["name"]
            is_cover = img.get("is_cover", False) if isinstance(img, dict) else False
            images.append(ProductImage(
                url=url,
                alt=alt,
                is_cover=is_cover,
                thumbnail_url=optimize_image_url(url, width=420)
            ))

        variants_raw = json.loads(r["variants_json"] or "[]")
        variants = []
        for var in variants_raw:
            variants.append(ProductVariant(
                id=str(var.get("id", "")),
                title=var.get("title", ""),
                price=float(var.get("price", r["price"])),
                regular_price=float(var.get("regular_price", r["regular_price"] or r["price"])),
                sku=var.get("sku", r["sku"]),
                stock_status=var.get("stock_status", r["stock_status"]),
                attributes=var.get("attributes", {})
            ))

        metadata = json.loads(r["metadata_json"] or "{}")

        return ProductDetail(
            id=r["id"],
            sku=r["sku"],
            name=r["name"],
            slug=r["slug"],
            description=r["description"] or "",
            short_description=r["short_description"] or "",
            price=r["price"],
            regular_price=r["regular_price"],
            currency=r["currency"],
            stock_status=r["stock_status"],
            stock_quantity=r["stock_quantity"],
            category_id=r["category_id"],
            category_name=r["category_name"] or "",
            images=images,
            variants=variants,
            metadata=metadata,
            source=r["source"],
            source_id=r["source_id"],
            source_url=r["source_url"] or "",
            is_featured=bool(r["is_featured"]),
            is_active=bool(r["is_active"]),
            created_at=str(r["created_at"]),
            updated_at=str(r["updated_at"])
        )

@router.get("/products/{id}/related", response_model=List[ProductSummary])
async def get_related_products(id: str, limit: int = 4, db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns related products from the same category or overall collection.
    """
    # Find current product category
    async with db.execute("SELECT category_id FROM products WHERE id = ?", (id,)) as cursor:
        row = await cursor.fetchone()
        cat_id = row["category_id"] if row else None

    query = """
    SELECT id, sku, name, slug, short_description, price, regular_price,
           currency, stock_status, category_id, category_name, images_json,
           variants_json, metadata_json, source, source_url, is_featured
    FROM products
    WHERE id != ? AND is_active = 1
    ORDER BY (CASE WHEN category_id = ? THEN 0 ELSE 1 END), RANDOM()
    LIMIT ?
    """
    async with db.execute(query, (id, cat_id, limit)) as cursor:
        rows = await cursor.fetchall()
        items = []
        for r in rows:
            images = json.loads(r["images_json"] or "[]")
            cover_img = images[0]["url"] if images else "/static/images/placeholder.svg"
            items.append(ProductSummary(
                id=r["id"],
                sku=r["sku"],
                name=r["name"],
                slug=r["slug"],
                short_description=r["short_description"] or "",
                price=r["price"],
                regular_price=r["regular_price"],
                currency=r["currency"],
                stock_status=r["stock_status"],
                category_id=r["category_id"],
                category_name=r["category_name"] or "",
                cover_image=cover_img,
                thumbnail_url=optimize_image_url(cover_img, width=420),
                image_count=len(images),
                source=r["source"],
                source_url=r["source_url"] or "",
                is_featured=bool(r["is_featured"])
            ))
        return items

@router.post("/analytics/event")
async def record_analytics_event(event: AnalyticsEventCreate, db: aiosqlite.Connection = Depends(get_db)):
    """
    Records customer interaction events (page view, product view, whatsapp enquiry, wishlist add).
    """
    await db.execute("""
        INSERT INTO analytics_events (event_type, product_id, metadata_json)
        VALUES (?, ?, ?)
    """, (event.event_type, event.product_id, json.dumps(event.metadata)))
    await db.commit()
    return {"status": "ok"}

@router.post("/ai-search")
async def ai_search_carpets(query: str = Query(..., min_length=2), db: aiosqlite.Connection = Depends(get_db)):
    """
    Free-tier AI semantic search & concierge advisor (Gemini/Groq integration).
    Interprets natural language queries (e.g. 'vintage red medallion for dining room')
    and returns matched products with styling suggestions.
    """
    from ..services.ai_concierge import ai_search_and_recommend
    
    # Fetch active products for context
    async with db.execute("""
        SELECT id, name, price, category_name, metadata_json FROM products WHERE is_active = 1 LIMIT 50
    """) as cursor:
        rows = await cursor.fetchall()
        products_context = []
        for r in rows:
            meta = json.loads(r["metadata_json"] or "{}")
            products_context.append({
                "id": r["id"],
                "name": r["name"],
                "price": r["price"],
                "category_name": r["category_name"],
                "material": meta.get("material", ""),
                "origin": meta.get("origin", "")
            })

    result = await ai_search_and_recommend(query, products_context)
    return result

