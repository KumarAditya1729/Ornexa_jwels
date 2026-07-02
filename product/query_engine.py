import argparse
import json
import os
import glob

class OrnexaQueryEngine:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.catalog = []
        self._load_data()

    def _load_data(self):
        json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
        # Exclude metrics files
        json_files = [f for f in json_files if not f.endswith("_metrics.json")]
        
        for jf in json_files:
            try:
                with open(jf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.catalog.extend(data)
            except Exception as e:
                print(f"Error loading {jf}: {e}")
                
        print(f"[QueryEngine] Loaded {len(self.catalog)} total items.")

    def search(self, category=None, metal=None, gemstone=None, style=None):
        results = []
        for item in self.catalog:
            match = True
            if category and category.lower() != str(item.get("category", "")).lower():
                match = False
            if metal and metal.lower() != str(item.get("metal_type", "")).lower():
                match = False
            
            if gemstone:
                gems = [str(g).lower() for g in item.get("gemstones", [])]
                if gemstone.lower() not in gems:
                    match = False
                    
            if style:
                styles = [str(s).lower() for s in item.get("style", [])]
                if style.lower() not in styles:
                    match = False
                    
            if match:
                results.append(item)
                
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORNEXA Query Engine")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--metal", type=str, help="Filter by metal")
    parser.add_argument("--gemstone", type=str, help="Filter by gemstone")
    parser.add_argument("--style", type=str, help="Filter by style")
    parser.add_argument("--data-dir", type=str, default="../ingestion/processed_data", help="Path to processed JSON directory")
    
    args = parser.parse_args()
    
    engine = OrnexaQueryEngine(args.data_dir)
    results = engine.search(
        category=args.category,
        metal=args.metal,
        gemstone=args.gemstone,
        style=args.style
    )
    
    print(f"\n--- Search Results ({len(results)} matches) ---")
    for r in results:
        print(f"\n> {r.get('product_name')} [{r.get('canonical_id')}]")
        print(f"  Category: {r.get('category')} | Subcategory: {r.get('subcategory')}")
        print(f"  Metal: {r.get('metal_type')} | Gems: {', '.join(r.get('gemstones', []))}")
        if r.get('style'):
            print(f"  Styles: {', '.join(r.get('style', []))}")
        print(f"  Price: {r.get('price')} {r.get('currency', 'INR')}")
        print(f"  Desc: {r.get('description')}")
    print()
