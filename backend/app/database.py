import sqlite3
import aiosqlite
import os
import json
import logging
from typing import AsyncGenerator
from .config import settings

logger = logging.getLogger("catalog_maker.database")

def ensure_db_dir():
    db_dir = os.path.dirname(settings.DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

def get_sync_db() -> sqlite3.Connection:
    ensure_db_dir()
    conn = sqlite3.connect(settings.DATABASE_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    ensure_db_dir()
    conn = await aiosqlite.connect(settings.DATABASE_PATH, timeout=20.0)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode = WAL")
    await conn.execute("PRAGMA synchronous = NORMAL")
    await conn.execute("PRAGMA cache_size = -64000")
    await conn.execute("PRAGMA temp_store = MEMORY")
    await conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        await conn.close()

def init_db():
    """Initializes tables, indexes, and default settings."""
    ensure_db_dir()
    with get_sync_db() as conn:
        cursor = conn.cursor()
        
        # Categories table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            image_url TEXT DEFAULT '',
            display_order INTEGER DEFAULT 0,
            is_visible INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_order ON categories(display_order, is_visible);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);")

        # Products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,              -- 'shopify' | 'woocommerce' | 'manual'
            source_id TEXT,                    -- external ID in source system
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            short_description TEXT DEFAULT '',
            price REAL NOT NULL DEFAULT 0.0,
            regular_price REAL DEFAULT 0.0,
            currency TEXT DEFAULT 'INR',
            stock_status TEXT DEFAULT 'instock', -- 'instock' | 'outofstock' | 'onbackorder'
            stock_quantity INTEGER DEFAULT 1,
            category_id TEXT,
            category_name TEXT DEFAULT '',
            images_json TEXT DEFAULT '[]',      -- JSON array of image URLs or objects
            variants_json TEXT DEFAULT '[]',    -- JSON array of variants (sizes, colors)
            metadata_json TEXT DEFAULT '{}',    -- Material, weave, knot count, origin, dimensions
            source_url TEXT DEFAULT '',         -- Link to original store
            is_featured INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            content_hash TEXT DEFAULT '',       -- SHA-256 for diff detection
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id, is_active);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_source ON products(source, source_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_status ON products(stock_status, is_active);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);")

        # Store Settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Sync Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_logs (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,               -- 'shopify' | 'woocommerce' | 'all'
            status TEXT NOT NULL,               -- 'running' | 'success' | 'failed'
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            duration_ms INTEGER DEFAULT 0,
            items_fetched INTEGER DEFAULT 0,
            items_created INTEGER DEFAULT 0,
            items_updated INTEGER DEFAULT 0,
            items_unchanged INTEGER DEFAULT 0,
            error_message TEXT DEFAULT '',
            details_json TEXT DEFAULT '{}'
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_logs_started ON sync_logs(started_at DESC);")

        # Product Audit / Change History
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            action TEXT NOT NULL,               -- 'created' | 'updated' | 'price_changed' | 'stock_changed' | 'deleted'
            changes_json TEXT DEFAULT '{}',
            actor TEXT DEFAULT 'system',        -- 'sync_shopify' | 'sync_woocommerce' | 'admin'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_product ON product_audit_log(product_id, created_at DESC);")

        # Analytics Events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,          -- 'page_view' | 'product_view' | 'whatsapp_single' | 'whatsapp_multi' | 'wishlist_add'
            product_id TEXT,
            metadata_json TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type, created_at DESC);")

        # Seed initial store settings if empty
        default_settings = [
            ("store_name", settings.DEFAULT_STORE_NAME),
            ("tagline", "Handcrafted Luxury Carpets & Rugs - Direct Artisan Gallery"),
            ("whatsapp_number", settings.DEFAULT_WHATSAPP),
            ("whatsapp_message_template", "Hi, I am interested in the following products:\n{product_list}\nPlease share more details and pricing."),
            ("active_design", settings.DEFAULT_DESIGN),
            ("currency", settings.DEFAULT_CURRENCY),
            ("currency_symbol", settings.DEFAULT_CURRENCY_SYMBOL),
            ("auto_sync_enabled", "1"),
            ("auto_sync_interval_minutes", str(settings.AUTO_SYNC_INTERVAL_MINUTES)),
            ("banner_announcement", "✨ Exclusive Hand-Knotted Silk & Wool Rugs Collection | Direct WhatsApp Inquiry & Fast Shipping"),
            ("banner_is_active", "1")
        ]
        for key, val in default_settings:
            cursor.execute("INSERT OR IGNORE INTO store_settings (key, value) VALUES (?, ?);", (key, val))

        conn.commit()
        logger.info("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
