from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Variant model (e.g. Size, Color, Pile)
class ProductVariant(BaseModel):
    id: str
    title: str
    price: float
    regular_price: Optional[float] = None
    sku: Optional[str] = None
    stock_status: str = "instock"
    attributes: Dict[str, str] = Field(default_factory=dict)

# Image model
class ProductImage(BaseModel):
    url: str
    alt: Optional[str] = ""
    is_cover: bool = False
    thumbnail_url: Optional[str] = None

# Category models
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    display_order: int = 0
    is_visible: bool = True

class CategoryResponse(CategoryBase):
    id: str
    product_count: int = 0

class CategoryCreateUpdate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    display_order: int = 0
    is_visible: bool = True

# Product models (Internal Catalog API format)
class ProductSummary(BaseModel):
    id: str
    sku: str
    name: str
    slug: str
    short_description: str = ""
    price: float
    regular_price: Optional[float] = None
    currency: str = "INR"
    stock_status: str = "instock"
    category_id: Optional[str] = None
    category_name: str = ""
    cover_image: str = ""
    thumbnail_url: str = ""
    image_count: int = 1
    variants_summary: List[str] = Field(default_factory=list)
    origin: Optional[str] = ""
    material: Optional[str] = ""
    source: str = "manual"
    source_url: str = ""
    is_featured: bool = False

class ProductDetail(BaseModel):
    id: str
    sku: str
    name: str
    slug: str
    description: str = ""
    short_description: str = ""
    price: float
    regular_price: Optional[float] = None
    currency: str = "INR"
    stock_status: str = "instock"
    stock_quantity: int = 1
    category_id: Optional[str] = None
    category_name: str = ""
    images: List[ProductImage] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "manual"
    source_id: Optional[str] = None
    source_url: str = ""
    is_featured: bool = False
    is_active: bool = True
    created_at: str
    updated_at: str

class ProductCreateUpdate(BaseModel):
    name: str
    sku: str
    slug: Optional[str] = None
    description: Optional[str] = ""
    short_description: Optional[str] = ""
    price: float
    regular_price: Optional[float] = None
    currency: str = "INR"
    stock_status: str = "instock"
    stock_quantity: int = 1
    category_id: Optional[str] = None
    images: List[Dict[str, Any]] = Field(default_factory=list)
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "manual"
    source_url: Optional[str] = ""
    is_featured: bool = False
    is_active: bool = True

class QuickUpdateProduct(BaseModel):
    price: Optional[float] = None
    regular_price: Optional[float] = None
    stock_status: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None

# Catalog Configuration
class CatalogConfig(BaseModel):
    store_name: str
    tagline: str
    whatsapp_number: str
    whatsapp_message_template: str
    active_design: str
    currency: str
    currency_symbol: str
    banner_announcement: str
    banner_is_active: bool
    total_products: int = 0
    total_categories: int = 0

class SettingsUpdate(BaseModel):
    store_name: Optional[str] = None
    tagline: Optional[str] = None
    whatsapp_number: Optional[str] = None
    whatsapp_message_template: Optional[str] = None
    active_design: Optional[str] = None
    banner_announcement: Optional[str] = None
    banner_is_active: Optional[bool] = None
    auto_sync_enabled: Optional[bool] = None
    auto_sync_interval_minutes: Optional[int] = None

# Paginated Response
class PaginatedProductsResponse(BaseModel):
    items: List[ProductSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

# Sync models
class SyncTriggerRequest(BaseModel):
    source: str = "all"  # 'shopify' | 'woocommerce' | 'all'
    force_full: bool = False
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

class SyncLogResponse(BaseModel):
    id: str
    source: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: int
    items_fetched: int
    items_created: int
    items_updated: int
    items_unchanged: int
    error_message: Optional[str] = ""
    details_json: Optional[Dict[str, Any]] = None

# Analytics Event model
class AnalyticsEventCreate(BaseModel):
    event_type: str
    product_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
