import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .config import settings
from .database import init_db
from .api.catalog import router as catalog_router
from .api.admin import router as admin_router
from .api.mock_sources import router as mock_router
from .services.scheduler import scheduler
from .services.shopify_sync import sync_shopify_catalog
from .services.woocommerce_sync import sync_woocommerce_catalog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("catalog_maker")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables and indexes exist
    logger.info("Initializing Catalog Maker database...")
    init_db()

    # Pre-seed with Shopify & WooCommerce initial sync if empty
    from .database import get_sync_db
    with get_sync_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        if count == 0:
            logger.info("Database is empty. Running initial sync for demonstration products...")
            await sync_shopify_catalog()
            await sync_woocommerce_catalog()
            logger.info("Initial sync completed: 100+ demo products loaded.")

    # Start background scheduler
    await scheduler.start()
    
    yield

    # Shutdown
    await scheduler.stop()
    logger.info("Catalog Maker shutdown completed.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Gzip compression for high speed
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(catalog_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(mock_router)

# Mount static frontend assets
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_catalog():
    """Serves the customer-facing fast mobile catalog"""
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin():
    """Serves the administrative management portal"""
    admin_path = os.path.join(TEMPLATES_DIR, "admin.html")
    return FileResponse(admin_path)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Catalog Maker",
        "version": settings.VERSION
    }
