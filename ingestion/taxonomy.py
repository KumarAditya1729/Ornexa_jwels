import re

# Comprehensive Category Mapping
CATEGORY_KEYWORDS = {
    "Earrings": ["earring", "jhumka", "jhumki", "chandbali", "stud", "hoop", "drop", "bali", "kanchain"],
    "Necklace": ["necklace", "chain", "pendant", "choker", "haar", "mala", "rani haar", "mangalsutra", "thali"],
    "Ring": ["ring", "band", "solitaire", "anguthi", "cocktail ring"],
    "Bracelet": ["bracelet", "bangle", "cuff", "kada", "chudi", "kangan"],
    "Bridal Set": ["bridal set", "wedding set", "choker set", "jewellery set", "necklace set"],
    "Waistbelt": ["vaddanam", "waistbelt", "kamarband", "kamarbandh", "oddiyanam"],
    "Anklet": ["payal", "anklet", "kolusu", "pajeb", "ghungroo"],
    "Armlet": ["bajuband", "armlet", "vanki", "baajubandh"],
    "Headpiece": ["maang tikka", "matha patti", "nethi chutti", "passa", "jhumar", "damini"]
}

# Subcategory extraction helps when a specific type is mentioned
SUBCATEGORY_KEYWORDS = [
    "jhumka", "jhumki", "chandbali", "choker", "mangalsutra", "thali", "rani haar", 
    "kada", "maang tikka", "matha patti", "nethi chutti", "passa", "vaddanam", 
    "bajuband", "payal", "stud", "hoop"
]

# Craft and Style Traditions
STYLE_KEYWORDS = {
    "Temple": ["temple", "nagas", "nakshi", "lakshmi", "god motif", "deity"],
    "Kundan": ["kundan", "kundan-meena", "pachi kundan"],
    "Polki": ["polki", "uncut diamond", "syndicate polki"],
    "Jadau": ["jadau", "jadtar"],
    "Meenakari": ["meenakari", "meena", "enamel", "enamelled", "bikaneri"],
    "Antique": ["antique", "oxidised", "vintage", "heritage"],
    "Contemporary": ["modern", "contemporary", "minimalist", "western"],
    "Traditional": ["traditional", "classic", "ethnic"]
}

METAL_KEYWORDS = ["Gold", "Silver", "Platinum", "Rose Gold", "White Gold", "Panchaloha", "Brass", "Copper", "Alloy"]
GEMSTONE_KEYWORDS = ["Diamond", "Ruby", "Emerald", "Sapphire", "Pearl", "Navaratna", "Coral", "Topaz", "Amethyst", "Kemp", "Spinel", "Tourmaline"]

def enhance_taxonomy(mapped_data):
    """Adds intelligence by inferring missing taxonomy fields from text."""
    title = str(mapped_data.get("product_name", "")).lower()
    description = str(mapped_data.get("description", "")).lower()
    combined_text = f"{title} {description}"

    # 1. Infer Category & Subcategory
    current_category = mapped_data.get("category", "")
    if not current_category or current_category.lower() in ["other", "jewelry", "jewellery", ""]:
        inferred_category = None
        
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in combined_text:
                    inferred_category = cat
                    break
            if inferred_category:
                break
                
        mapped_data["category"] = inferred_category if inferred_category else "Uncategorized"

    # Infer Subcategory
    if not mapped_data.get("subcategory"):
        inferred_subcategory = None
        for sub in SUBCATEGORY_KEYWORDS:
            if sub in combined_text:
                inferred_subcategory = sub.title()
                break
        if inferred_subcategory:
            mapped_data["subcategory"] = inferred_subcategory

    # 2. Infer Style Traditions (Multi-craft Support)
    detected_styles = []
    for style, keywords in STYLE_KEYWORDS.items():
        for kw in keywords:
            if kw in combined_text and style not in detected_styles:
                detected_styles.append(style)
                break
                
    existing_styles = mapped_data.get("style")
    if existing_styles and isinstance(existing_styles, list):
        # merge existing with detected
        mapped_data["style"] = list(set(existing_styles + detected_styles))
    elif existing_styles and isinstance(existing_styles, str):
        mapped_data["style"] = list(set([existing_styles] + detected_styles))
    else:
        mapped_data["style"] = detected_styles

    # 3. Extract Metal
    if not mapped_data.get("metal_type"):
        for metal in METAL_KEYWORDS:
            if metal.lower() in combined_text:
                mapped_data["metal_type"] = metal
                break

    # 4. Extract Gemstones
    existing_gems = mapped_data.get("gemstones", "")
    if isinstance(existing_gems, str):
        existing_gems = [g.strip() for g in existing_gems.split('|') if g.strip()]
    elif not existing_gems:
        existing_gems = []
        
    for gem in GEMSTONE_KEYWORDS:
        if gem.lower() in combined_text and gem not in existing_gems:
            existing_gems.append(gem)
            
    mapped_data["gemstones"] = existing_gems

    return mapped_data

def generate_semantic_title(description):
    if not description:
        return ""
    
    desc_lower = description.lower()
    
    # 1. Extract Color/Motif (heuristic)
    colors = ["blue", "red", "green", "pink", "black", "white", "yellow", "purple", "floral"]
    found_color = None
    for c in colors:
        if c in desc_lower:
            found_color = c.title()
            break
            
    # 2. Extract Style
    found_styles = []
    for style, keywords in STYLE_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            found_styles.append(style)
            
    # 3. Extract Metal
    found_metal = None
    for metal in METAL_KEYWORDS:
        if metal.lower() in desc_lower:
            found_metal = metal
            break
            
    # 4. Extract Gemstone
    found_gem = None
    for gem in GEMSTONE_KEYWORDS:
        if gem.lower() in desc_lower:
            found_gem = gem
            break
            
    # 5. Extract Category
    found_cat = None
    for cat, keywords in CATEGORY_KEYWORDS.items():
        # Match exact word or prefix
        if any(kw in desc_lower for kw in keywords):
            found_cat = cat
            break
            
    parts = []
    for s in found_styles:
        parts.append(s)
    if found_color and not found_styles: parts.append(found_color)
    if found_metal: parts.append(found_metal)
    if found_gem: parts.append(found_gem)
    
    if found_cat:
        parts.append(found_cat)
    else:
        # If no category found but we found something else, append 'Item'
        if parts:
            parts.append("Item")
            
    if parts:
        # Deduplicate
        unique_parts = []
        for p in parts:
            if p not in unique_parts:
                unique_parts.append(p)
        return " ".join(unique_parts)
    
    return ""
