DATASET_PROFILES = {
    "cartier": {
        "identifiers": ["ref", "categorie", "title", "price"],
        "mapping": {
            "title": "product_name",
            "ref": "product_url",
            "price": "price",
            "image": "images",
            "categorie": "category",
            "description": "description",
            "tags": "collection_name"
        }
    },
    "kaggle_jewelry": {
        "identifiers": ["Product Name", "Cost", "Image_Path"],
        "mapping": {
            "Product Name": "product_name",
            "Cost": "price",
            "Image_Path": "images",
            "Type": "category"
        }
    },
    "kaggle_images": {
        "identifiers": ["image_path", "description"],
        "mapping": {
            "image_path": "images",
            "description": "description"
        }
    },
    "kaggle_events": {
        "identifiers": ["event_time", "event_type", "product_id", "category_code", "brand", "price", "user_id"],
        "mapping": {
            "event_time": "event_time",
            "user_id": "user_id",
            "product_id": "product_id",
            "price": "price",
            "category_code": "category",
            "metal": "metal",
            "gemstone": "gemstone"
        }
    },
    "default_ornexa": {
        "identifiers": ["product_name", "product_url", "images", "price", "category"],
        "mapping": {
            "product_name": "product_name",
            "product_url": "product_url",
            "images": "images",
            "category": "category",
            "subcategory": "subcategory",
            "metal_type": "metal_type",
            "purity": "purity",
            "gemstones": "gemstones",
            "weight": "weight",
            "price": "price",
            "currency": "currency",
            "gender": "gender",
            "occasion": "occasion",
            "description": "description",
            "collection_name": "collection_name"
        }
    }
}

def auto_detect_dataset(headers):
    """Detects which dataset profile matches the CSV headers."""
    header_set = set(headers)
    for profile_name, config in DATASET_PROFILES.items():
        if all(req in header_set for req in config["identifiers"]):
            return profile_name
    return None

def apply_profile(row, profile_name):
    """Maps raw row fields to ORNEXA schema fields."""
    if not profile_name or profile_name not in DATASET_PROFILES:
        return row  # Fallback: return as-is
    
    mapping = DATASET_PROFILES[profile_name]["mapping"]
    mapped_data = {}
    
    for raw_field, ornexa_field in mapping.items():
        val = row.get(raw_field)
        if val is not None:
            # Handle special field transformations
            if ornexa_field == "price" and isinstance(val, str):
                # Clean currency symbols
                val = val.replace('$', '').replace('€', '').replace(',', '').strip()
                try:
                    val = float(val)
                except ValueError:
                    val = 0.0
            
            # Construct a fake URL for cartier if missing
            if ornexa_field == "product_url" and profile_name == "cartier" and val:
                 val = f"https://www.cartier.com/en-us/{val}.html"
                 
            # Prepend domain for Cartier images
            if ornexa_field == "images" and profile_name == "cartier" and val:
                val = f"https://www.cartier.com{val}"
                 
            mapped_data[ornexa_field] = val
            
    # Fallbacks for specific datasets to pass strict validation
    if profile_name == "kaggle_images":
        if "price" not in mapped_data:
            mapped_data["price"] = 0.0
            
    # Apply semantic title generation for missing product_name (skip for commerce events)
    if "product_name" not in mapped_data and profile_name != "kaggle_events":
        from taxonomy import generate_semantic_title
        desc = mapped_data.get("description", "")
        cat = mapped_data.get("category", "")
        
        # Try description first, or use category
        title = generate_semantic_title(desc) if desc else ""
        if not title and cat:
            title = generate_semantic_title(cat)
            
        if title:
            mapped_data["product_name"] = title
        else:
            fallback_cat = cat if cat else "Item"
            mapped_data["product_name"] = f"Unnamed {fallback_cat}"
            
    # Default URL if completely missing (schema requires HttpUrl)
    if "product_url" not in mapped_data or not mapped_data["product_url"]:
        mapped_data["product_url"] = "https://ornexa.com/placeholder"
        
    return mapped_data
