import unittest
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.database import init_db, get_sync_db
from app.services.diff_engine import compute_product_hash, detect_changes
from app.services.shopify_sync import sync_shopify_catalog
from app.api.mock_sources import LIVE_SHOPIFY_STORE

class TestSyncEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_content_hashing_consistency(self):
        prod_a = {"name": "Test Carpet", "price": 50000, "sku": "TC-01", "stock_status": "instock"}
        prod_b = {"name": "Test Carpet", "price": 50000, "sku": "TC-01", "stock_status": "instock"}
        prod_c = {"name": "Test Carpet", "price": 55000, "sku": "TC-01", "stock_status": "instock"}

        hash_a = compute_product_hash(prod_a)
        hash_b = compute_product_hash(prod_b)
        hash_c = compute_product_hash(prod_c)

        self.assertEqual(hash_a, hash_b, "Identical products must produce identical hashes")
        self.assertNotEqual(hash_a, hash_c, "Price difference must change product hash")

    def test_deduplication_and_idempotent_sync(self):
        # First sync
        res1 = asyncio.run(sync_shopify_catalog())
        created_first = res1["items_created"]
        
        # Second sync with no changes should detect unchanged items without creating duplicates
        res2 = asyncio.run(sync_shopify_catalog())
        self.assertEqual(res2["items_created"], 0, "Second sync must not create duplicates")
        self.assertGreater(res2["items_unchanged"], 40, "Second sync must identify products as unchanged")

    def test_source_update_reflection(self):
        # Simulate an external price reduction on the source store
        target_product = LIVE_SHOPIFY_STORE[0]
        original_price = target_product["variants"][0]["price"]
        new_test_price = "225000.00"
        target_product["variants"][0]["price"] = new_test_price

        # Run sync
        res = asyncio.run(sync_shopify_catalog())
        self.assertGreaterEqual(res["items_updated"], 1, "Sync must detect the modified product and update it")

        # Verify DB reflects the new price
        with get_sync_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT price FROM products WHERE sku = ?", (target_product["variants"][0]["sku"],))
            row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(float(row[0]), 225000.00, "Product price in database must reflect the external change")

        # Restore original price
        target_product["variants"][0]["price"] = original_price

if __name__ == "__main__":
    unittest.main()
