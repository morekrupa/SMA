import unittest
import asyncio
import os
import sys

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.database import init_db, get_sync_db
from app.services.shopify_sync import sync_shopify_catalog
from app.services.woocommerce_sync import sync_woocommerce_catalog

class TestCatalogAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        asyncio.run(sync_shopify_catalog())
        asyncio.run(sync_woocommerce_catalog())

    def test_database_has_products(self):
        with get_sync_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM products")
            total = cur.fetchone()[0]
            self.assertGreaterEqual(total, 100, f"Expected at least 100 products (50 Shopify + 50 WooCommerce), got {total}")

    def test_shopify_products_loaded(self):
        with get_sync_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM products WHERE source = 'shopify'")
            shp_count = cur.fetchone()[0]
            self.assertGreaterEqual(shp_count, 50, f"Expected at least 50 Shopify products, got {shp_count}")

    def test_woocommerce_products_loaded(self):
        with get_sync_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM products WHERE source = 'woocommerce'")
            wc_count = cur.fetchone()[0]
            self.assertGreaterEqual(wc_count, 50, f"Expected at least 50 WooCommerce products, got {wc_count}")

    def test_categories_created(self):
        with get_sync_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM categories")
            cat_count = cur.fetchone()[0]
            self.assertGreaterEqual(cat_count, 5, f"Expected at least 5 categories, got {cat_count}")

if __name__ == "__main__":
    unittest.main()
