import os
import glob
import csv
import json
from collections import defaultdict

# Keywords for auto-mapping
MAPPING_HEURISTICS = {
    "product_name": ["title", "name", "productname", "item_name"],
    "product_url": ["url", "link", "producturl", "page_url"],
    "price": ["cost", "price", "priceusd", "amount", "mrp"],
    "images": ["image_path", "image", "img", "picture", "photo", "imageurl"],
    "category": ["category", "type", "department", "category_label"],
    "description": ["description", "desc", "details"],
    "metal_type": ["metal", "material"],
    "collection_name": ["collection", "tags", "brand"]
}

def suggest_mappings(headers):
    """Suggests ORNEXA schema fields for given raw headers."""
    suggestions = {}
    confidence_score = 0
    mapped_count = 0
    
    for header in headers:
        normalized_header = str(header).lower().strip()
        matched = False
        for ornexa_field, keywords in MAPPING_HEURISTICS.items():
            if any(kw in normalized_header for kw in keywords):
                suggestions[header] = ornexa_field
                matched = True
                mapped_count += 1
                break
        if not matched:
            suggestions[header] = "UNKNOWN"
            
    if headers:
        confidence_score = round(mapped_count / len(headers), 2)
        
    return suggestions, confidence_score

def analyze_dataset(csv_path):
    """Reads a CSV file to extract headers, samples, and row counts."""
    headers = []
    samples = defaultdict(list)
    row_count = 0
    
    try:
        with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            
            # Read Headers
            try:
                headers = next(reader)
            except StopIteration:
                return {"error": "Empty file"}
                
            # Read Rows
            for i, row in enumerate(reader):
                row_count += 1
                if i < 3: # Capture up to 3 sample rows
                    for j, val in enumerate(row):
                        if j < len(headers):
                            header_name = headers[j]
                            if val.strip():
                                samples[header_name].append(val.strip())
                                
    except Exception as e:
        return {"error": str(e)}

    # Deduplicate samples
    clean_samples = {k: list(set(v)) for k, v in samples.items()}
    
    suggestions, confidence = suggest_mappings(headers)
    
    return {
        "dataset_name": os.path.basename(csv_path),
        "filepath": csv_path,
        "rows": row_count,
        "columns": headers,
        "sample_values": clean_samples,
        "candidate_mappings": suggestions,
        "mapping_confidence": confidence
    }

def scan_directory(base_dir):
    """Scans for CSVs and generates the sniffer report."""
    print(f"Scanning {base_dir} for datasets...")
    csv_files = glob.glob(os.path.join(base_dir, "**", "*.csv"), recursive=True)
    
    report = {"datasets": []}
    
    for csv_file in csv_files:
        print(f"Sniffing {csv_file}...")
        analysis = analyze_dataset(csv_file)
        report["datasets"].append(analysis)
        
    return report

if __name__ == "__main__":
    base_dir = "processed_data"
    report = scan_directory(base_dir)
    
    output_path = "sniffer_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
        
    print(f"\n--- ORNEXA Dataset Sniffer Report ---")
    for ds in report["datasets"]:
        if "error" in ds:
            print(f"❌ {ds.get('filepath', 'Unknown')}: {ds['error']}")
            continue
            
        print(f"📁 {ds['dataset_name']}")
        print(f"   Rows: {ds['rows']}")
        print(f"   Columns: {len(ds['columns'])}")
        print(f"   Auto-Map Confidence: {ds['mapping_confidence'] * 100}%")
        
        # Display unknown columns
        unknowns = [k for k, v in ds['candidate_mappings'].items() if v == "UNKNOWN"]
        if unknowns:
            print(f"   Unmapped columns: {', '.join(unknowns[:5])}{'...' if len(unknowns) > 5 else ''}")
        print("-" * 40)
        
    print(f"\nDetailed report saved to {output_path}")
