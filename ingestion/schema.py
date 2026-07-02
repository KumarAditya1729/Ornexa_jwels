from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class ProductSchema(BaseModel):
    product_name: str
    product_url: HttpUrl
    images: List[HttpUrl]
    category: str
    subcategory: Optional[str] = None
    style: Optional[List[str]] = []
    metal_type: Optional[str] = None
    purity: Optional[str] = None
    gemstones: Optional[List[str]] = []
    weight: Optional[float] = None  # In grams
    price: float
    currency: str = "INR"
    gender: Optional[str] = None
    occasion: Optional[str] = None
    description: Optional[str] = None
    collection_name: Optional[str] = None
    
    # Intelligence Tracking Fields
    source_dataset: Optional[str] = "unknown"
    mapping_confidence: float = 0.0
    taxonomy_confidence: float = 0.0
    canonical_id: Optional[str] = None

class CommerceEventSchema(BaseModel):
    event_time: str
    user_id: str
    product_id: str
    price: float
    category: Optional[str] = None
    metal: Optional[str] = None
    gemstone: Optional[str] = None

