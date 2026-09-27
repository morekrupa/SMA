import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    PROJECT_NAME: str = "Catalog Maker - High-Speed Product Catalog Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/catalog.db")))
    
    # Store defaults
    DEFAULT_WHATSAPP: str = "+919876543210"
    DEFAULT_STORE_NAME: str = "Rajdhani Artisans & Digital Carpets"
    DEFAULT_DESIGN: str = "rajdhani"  # "rajdhani" | "nordic"
    DEFAULT_CURRENCY: str = "INR"
    DEFAULT_CURRENCY_SYMBOL: str = "₹"
    
    # Sync settings
    AUTO_SYNC_INTERVAL_MINUTES: int = 15
    SHOPIFY_API_KEY: Optional[str] = os.getenv("SHOPIFY_API_KEY", "")
    SHOPIFY_STORE_URL: Optional[str] = os.getenv("SHOPIFY_STORE_URL", "")
    WOOCOMMERCE_URL: Optional[str] = os.getenv("WOOCOMMERCE_URL", "")
    WOOCOMMERCE_KEY: Optional[str] = os.getenv("WOOCOMMERCE_KEY", "")
    WOOCOMMERCE_SECRET: Optional[str] = os.getenv("WOOCOMMERCE_SECRET", "")

settings = Settings()
