import csv
import json
import os
import requests
import zipfile
import glob
import shutil
from urllib.parse import urlparse
from pydantic import ValidationError
from schema import ProductSchema, CommerceEventSchema
from collections import Counter
from mapper import auto_detect_dataset, apply_profile
from taxonomy import enhance_taxonomy, CATEGORY_KEYWORDS, STYLE_KEYWORDS
from dedupe import Deduplicator

def download_image(url: str, save_dir: str) -> str:
    """Download an image and return the local path."""
    os.makedirs(save_dir, exist_ok=True)
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename or '.' not in filename:
        filename = f"image_{hash(url)}.jpg"
    
    local_path = os.path.join(save_dir, filename)
    
    if os.path.exists(local_path):
        return local_path

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return local_path
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return ""

def process_feed(csv_path: str, output_json_path: str, images_base_dir: str):
    valid_products = []
    errors = []
    
    metrics = {
        "raw_rows_scanned": 0,
        "rows_mapped": 0,
        "product_rows_validated": 0,
        "commerce_rows_validated": 0,
        "rows_rejected": 0,
        "categories_detected": Counter(),
        "styles_detected": Counter(),
        "metals_detected": Counter(),
        "gemstones_detected": Counter(),
        "missing_images": 0,
        "duplicates": 0,
        "fields_populated": 0,
        "total_fields": 0,
        "mapping_conf_sum": 0.0,
        "taxonomy_conf_sum": 0.0
    }
    
    deduplicator = Deduplicator()

    with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
        if "jewelry.csv" in csv_path:
            fieldnames = ["event_time", "event_type_id", "product_id", "unknown_1", "category_id", "category_code", "unknown_2", "price", "user_id", "brand", "color", "metal", "gemstone"]
            reader = csv.DictReader(f, fieldnames=fieldnames)
        else:
            reader = csv.DictReader(f)
        
        # 1. Auto-detect dataset profile
        headers = reader.fieldnames or []
        profile_name = auto_detect_dataset(headers)
        if profile_name:
            print(f"Detected profile '{profile_name}' for {csv_path}")
        else:
            print(f"No profile matched for {csv_path}. Attempting raw mapping...")

        for row_idx, row in enumerate(reader, start=1):
            metrics["raw_rows_scanned"] += 1
            try:
                # 2. Map raw row using dataset profile
                mapped_row = apply_profile(row, profile_name)
                
                if mapped_row.get("product_name"):
                    metrics["rows_mapped"] += 1
                    
                mapping_conf = len([v for v in mapped_row.values() if v]) / max(len(headers), 1)
                
                # 3. Enhance with ORNEXA taxonomy intelligence
                enhanced_data = enhance_taxonomy(mapped_row)
                
                tax_conf = 1.0 if enhanced_data.get("category") not in ["Uncategorized", ""] else 0.5
                
                # Add Tracking Info
                enhanced_data["source_dataset"] = profile_name or "unknown"
                enhanced_data["mapping_confidence"] = round(mapping_conf, 2)
                enhanced_data["taxonomy_confidence"] = tax_conf
                
                metrics["mapping_conf_sum"] += mapping_conf
                metrics["taxonomy_conf_sum"] += tax_conf
                
                # Preprocess arrays (images)
                if isinstance(enhanced_data.get('images'), str):
                    enhanced_data['images'] = [img.strip() for img in enhanced_data['images'].split('|') if img.strip()]
                elif not enhanced_data.get('images'):
                    enhanced_data['images'] = ["https://ornexa.com/placeholder.jpg"]
                    metrics["missing_images"] += 1
                    
                # 4. Validate using Pydantic
                if profile_name == "kaggle_events":
                    event = CommerceEventSchema(**enhanced_data)
                    valid_products.append(event.model_dump(mode='json'))
                    metrics["commerce_rows_validated"] += 1
                    
                    if event.category: metrics["categories_detected"][event.category] += 1
                    if event.metal: metrics["metals_detected"][event.metal] += 1
                    if event.gemstone: metrics["gemstones_detected"][event.gemstone] += 1
                else:
                    product = ProductSchema(**enhanced_data)
                    
                    # If valid, process images
                    safe_product_name = "".join([c if c.isalnum() else "_" for c in product.product_name])
                    product_img_dir = os.path.join(images_base_dir, safe_product_name)
                    
                    local_image_paths = []
                    for img_url in product.images:
                        if "placeholder" not in str(img_url):
                            local_path = download_image(str(img_url), product_img_dir)
                            if local_path:
                                local_image_paths.append(local_path)
                    
                    # Convert back to dict for JSON output
                    product_dict = product.model_dump(mode='json')
                    product_dict['local_images'] = local_image_paths
                    
                    # Deduplication for products only
                    product_dict = deduplicator.dedupe(product_dict)
                    
                    valid_products.append(product_dict)
                    metrics["product_rows_validated"] += 1
                    
                    if product.category: metrics["categories_detected"][product.category] += 1
                    if product.style: 
                        for s in product.style: metrics["styles_detected"][s] += 1
                    if product.metal_type: metrics["metals_detected"][product.metal_type] += 1
                    if product.gemstones: 
                        for g in product.gemstones: metrics["gemstones_detected"][g] += 1
                        
                    non_nulls = sum(1 for v in product_dict.values() if v)
                    metrics["fields_populated"] += non_nulls
                    metrics["total_fields"] += len(product_dict)

            except ValidationError as e:
                metrics["rows_rejected"] += 1
                if len(errors) < 5:
                    print(f"Validation error in row {row_idx}: {e}")
                elif len(errors) == 5:
                    print(f"Further validation errors suppressed...")
                errors.append({"row": row_idx, "error": "Validation Error"})
            except Exception as e:
                metrics["rows_rejected"] += 1
                if len(errors) < 5:
                    print(f"Unexpected error in row {row_idx}: {e}")
                elif len(errors) == 5:
                    print(f"Further errors suppressed...")
                errors.append({"row": row_idx, "error": "Unexpected Error"})
                
    # Calculate duplicates
    metrics["duplicates"] = metrics["product_rows_validated"] - len(deduplicator.clusters) if metrics["product_rows_validated"] > 0 else 0

    validated_prods = metrics["product_rows_validated"]
    validated_events = metrics["commerce_rows_validated"]
    total_valid = validated_prods + validated_events
    canonical_prods = len(deduplicator.clusters) if validated_prods > 0 else 0
    
    knowledge_yield = canonical_prods / metrics["raw_rows_scanned"] if metrics["raw_rows_scanned"] > 0 else 0
    knowledge_density = metrics["fields_populated"] / metrics["total_fields"] if metrics["total_fields"] > 0 else 0
    
    avg_mapping = metrics["mapping_conf_sum"] / metrics["raw_rows_scanned"] if metrics["raw_rows_scanned"] > 0 else 0
    avg_tax = metrics["taxonomy_conf_sum"] / metrics["raw_rows_scanned"] if metrics["raw_rows_scanned"] > 0 else 0
    
    # Taxonomy Coverage Score
    master_terms = set(CATEGORY_KEYWORDS.keys()).union(set(STYLE_KEYWORDS.keys()))
    detected_terms = set(metrics["categories_detected"].keys()).union(set(metrics["styles_detected"].keys()))
    
    covered_cats = list(master_terms.intersection(detected_terms))
    missing_cats = list(master_terms.difference(detected_terms))
    coverage_score = len(covered_cats) / len(master_terms) if master_terms else 0
    
    # OIS Calculation
    avg_confidence = (avg_mapping + avg_tax) / 2
    ois_score = (knowledge_yield * 20) + (knowledge_density * 30) + (coverage_score * 30) + (avg_confidence * 20)

    report = {
        "validated_products": validated_prods,
        "validated_events": validated_events,
        "canonical_products": canonical_prods,
        "knowledge_yield": round(knowledge_yield, 2),
        "knowledge_density": round(knowledge_density, 2),
        "coverage_score": round(coverage_score, 2),
        "mapping_confidence": round(avg_mapping, 2),
        "taxonomy_confidence": round(avg_tax, 2),
        "ois": round(ois_score, 1),
        "covered_categories": covered_cats,
        "missing_categories": missing_cats,
        "top_categories": [k for k, v in metrics["categories_detected"].most_common(5)],
        "top_metals": [k for k, v in metrics["metals_detected"].most_common(5)],
        "top_gemstones": [k for k, v in metrics["gemstones_detected"].most_common(5)]
    }

    # Export to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(valid_products, f, indent=4)
        
    metrics_path = output_json_path.replace(".json", "_metrics.json")
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
    
    print(f"\n--- ORNEXA Ingestion Report ---")
    for k, v in report.items():
        print(f"{k}: {v}")
    print(f"-------------------------------\n")

def process_zip_file(zip_path: str, output_base_dir: str, images_base_dir: str):
    """Extracts a zip file and processes any CSV feeds inside it."""
    zip_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_dir = os.path.join(output_base_dir, f"extracted_{zip_name}")
    
    print(f"Extracting {zip_path} to {extract_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
        
    csv_files = glob.glob(os.path.join(extract_dir, "**", "*.csv"), recursive=True)
    if not csv_files:
        print(f"No CSV files found in {zip_path}.")
        return

    for csv_file in csv_files:
        csv_filename = os.path.basename(csv_file)
        json_output_path = os.path.join(output_base_dir, f"{zip_name}_{csv_filename}.json")
        print(f"Processing CSV from zip: {csv_file}")
        process_feed(csv_file, json_output_path, images_base_dir)

    # Optionally clean up extracted files
    # shutil.rmtree(extract_dir)

if __name__ == "__main__":
    csv_file = "sample_data.csv"
    json_file = "ornexa_catalog.json"
    images_dir = "product_images"
    output_dir = "processed_data"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Process normal standalone CSV
    if os.path.exists(csv_file):
        print("Starting standalone CSV ingestion pipeline...")
        process_feed(csv_file, os.path.join(output_dir, json_file), images_dir)

    # 2. Process any zip files in the parent (ORNEXA JEWLS) directory or current directory
    # parent_dir = os.path.dirname(os.getcwd())
    # zip_files = glob.glob(os.path.join(parent_dir, "*.zip")) + glob.glob("*.zip")
    # for zf in zip_files:
    #     print(f"\nFound dataset archive: {zf}")
    #     process_zip_file(zf, output_dir, images_dir)
