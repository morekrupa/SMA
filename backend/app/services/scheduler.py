import asyncio
import logging
from .shopify_sync import sync_shopify_catalog
from .woocommerce_sync import sync_woocommerce_catalog
from ..database import get_sync_db

logger = logging.getLogger("catalog_maker.scheduler")

class CatalogScheduler:
    def __init__(self):
        self._running = False
        self._task = None

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("CatalogScheduler background sync worker started.")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("CatalogScheduler stopped.")

    async def _run_loop(self):
        while self._running:
            try:
                # Read interval and enabled setting from database
                enabled = True
                interval_minutes = 15
                with get_sync_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT key, value FROM store_settings WHERE key IN ('auto_sync_enabled', 'auto_sync_interval_minutes')")
                    for row in cursor.fetchall():
                        if row["key"] == "auto_sync_enabled":
                            enabled = (row["value"] == "1")
                        elif row["key"] == "auto_sync_interval_minutes":
                            try:
                                interval_minutes = int(row["value"])
                            except ValueError:
                                interval_minutes = 15

                if enabled:
                    logger.info("Running automatic scheduled sync for Shopify and WooCommerce...")
                    await sync_shopify_catalog()
                    await sync_woocommerce_catalog()
                
                await asyncio.sleep(interval_minutes * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during scheduled sync run: {e}")
                await asyncio.sleep(60)

scheduler = CatalogScheduler()
