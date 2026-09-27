from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional, Dict, Any
import copy
from ..data.seed_shopify import get_shopify_products
from ..data.seed_woocommerce import get_woocommerce_products

router = APIRouter(prefix="/mock-source", tags=["Mock External Sources"])

# In-memory mutable copies to simulate real-time source edits
LIVE_SHOPIFY_STORE = copy.deepcopy(get_shopify_products())
LIVE_WOOCOMMERCE_STORE = copy.deepcopy(get_woocommerce_products())

@router.get("/shopify/admin/api/2024-01/products.json")
async def mock_shopify_products(limit: int = 250, since_id: Optional[int] = None):
    """
    Simulates official Shopify REST Admin API endpoint:
    GET https://{shop}.myshopify.com/admin/api/2024-01/products.json
    """
    products = LIVE_SHOPIFY_STORE
    if since_id:
        products = [p for p in products if p["id"] > since_id]
    return {"products": products[:limit]}

@router.get("/woocommerce/wp-json/wc/v3/products")
async def mock_woocommerce_products(per_page: int = 100, page: int = 1):
    """
    Simulates official WooCommerce REST API endpoint:
    GET https://{shop}/wp-json/wc/v3/products
    """
    start = (page - 1) * per_page
    end = start + per_page
    return LIVE_WOOCOMMERCE_STORE[start:end]

@router.post("/simulate/modify-product")
async def simulate_source_modification(payload: Dict[str, Any] = Body(...)):
    """
    Simulate a price or stock update in the external source (Shopify or WooCommerce).
    Requirement 19.9: "Show a source product update being reflected in the catalog."
    """
    source = payload.get("source", "shopify")
    field = payload.get("field", "price")
    new_value = payload.get("new_value", 99999)
    
    if source == "shopify":
        prod = LIVE_SHOPIFY_STORE[0]
        if field == "price":
            prod["variants"][0]["price"] = str(new_value)
        elif field == "stock":
            prod["variants"][0]["inventory_quantity"] = int(new_value)
        elif field == "title":
            prod["title"] = str(new_value)
        return {
            "success": True,
            "message": f"Updated Shopify source product #{prod['id']} ({prod['title']}) {field} to {new_value}",
            "product_id": prod["id"],
            "sku": prod["variants"][0]["sku"],
            "new_value": new_value
        }
    elif source == "woocommerce":
        prod = LIVE_WOOCOMMERCE_STORE[0]
        if field == "price":
            prod["price"] = str(new_value)
            prod["regular_price"] = str(float(new_value) + 5000)
        elif field == "stock":
            prod["stock_quantity"] = int(new_value)
            prod["stock_status"] = "instock" if int(new_value) > 0 else "outofstock"
        elif field == "name":
            prod["name"] = str(new_value)
        return {
            "success": True,
            "message": f"Updated WooCommerce source product #{prod['id']} ({prod['name']}) {field} to {new_value}",
            "product_id": prod["id"],
            "sku": prod["sku"],
            "new_value": new_value
        }
    else:
        raise HTTPException(status_code=400, detail="Source must be 'shopify' or 'woocommerce'")
