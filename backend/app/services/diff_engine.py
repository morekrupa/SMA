import hashlib
import json
from typing import Dict, Any, Tuple, Optional

def compute_product_hash(product_dict: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 hash of a product's synchronized fields.
    If the hash matches what's stored in the database, the product is UNCHANGED.
    If it differs, we detect granular field differences.
    """
    normalized = {
        "name": product_dict.get("name", "").strip(),
        "price": float(product_dict.get("price", 0.0)),
        "regular_price": float(product_dict.get("regular_price", 0.0) or 0.0),
        "stock_status": product_dict.get("stock_status", "instock"),
        "stock_quantity": int(product_dict.get("stock_quantity", 0)),
        "description": product_dict.get("description", "").strip(),
        "category_name": product_dict.get("category_name", "").strip(),
        "images": sorted([img.get("url", "") if isinstance(img, dict) else str(img) for img in product_dict.get("images", [])]),
        "variants": product_dict.get("variants", [])
    }
    dumped = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

def detect_changes(existing_product: Dict[str, Any], incoming_product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identifies exact fields that changed between existing DB record and incoming sync record.
    """
    changes = {}
    fields_to_check = ["price", "regular_price", "stock_status", "stock_quantity", "name", "description", "category_name"]
    for field in fields_to_check:
        old_val = existing_product.get(field)
        new_val = incoming_product.get(field)
        if str(old_val) != str(new_val):
            changes[field] = {"old": old_val, "new": new_val}
            
    # Check images change
    old_imgs = existing_product.get("images_json", "[]")
    new_imgs = json.dumps(incoming_product.get("images", []))
    if old_imgs != new_imgs:
        changes["images"] = "Images updated"

    return changes
