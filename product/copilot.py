import os
import json
import argparse
from collections import Counter

from product.vision_classifier import OrnexaVisionClassifier
from product.query_engine import OrnexaQueryEngine
from product.knowledge_explorer import OrnexaKnowledgeExplorer

class OrnexaCopilot:
    def __init__(self, 
                 weights_path="runs/classify/runs/ornexa_vision/weights/best.pt",
                 data_dir="../ingestion/processed_data",
                 kg_path="product/knowledge_graph.json"):
        """
        Initializes the Copilot by orchestrating all three AI layers.
        """
        print("[Copilot] Initializing Vision Layer...")
        self.vision = OrnexaVisionClassifier(weights_path)
        
        print("[Copilot] Initializing Commerce Layer...")
        self.search = OrnexaQueryEngine(data_dir)
        
        print("[Copilot] Initializing Knowledge Layer...")
        self.knowledge = OrnexaKnowledgeExplorer()
        
    def analyze_image(self, image_path: str):
        """
        Takes an image, runs vision, searches commerce, and extracts knowledge.
        """
        # 1. Vision
        vision_result = self.vision.classify(image_path)
        if isinstance(vision_result, str) and vision_result.startswith("Error"):
            return {"error": vision_result}
            
        category = vision_result["predicted_category"]
        confidence = vision_result["confidence"]
        
        # 2. Commerce Search
        products = self.search.search(category=category)
        
        # Sort or sample products (for now we just take the first 5)
        # Real-world we'd use embeddings to find visually similar ones
        top_products = products[:5]
        
        # Extract implied attributes from the most representative products
        # This simulates a multi-label model by assuming the user uploaded
        # a standard representation of the category.
        styles = []
        metals = []
        for p in top_products:
            if p.get("style"):
                styles.extend(p["style"])
            if p.get("metal_type"):
                metals.append(p["metal_type"])
                
        # Get most common style and metal
        inferred_style = [Counter(styles).most_common(1)[0][0]] if styles else []
        inferred_metal = Counter(metals).most_common(1)[0][0] if metals else "Unknown"
        
        # Strip verbose product data for clean output
        clean_products = []
        for p in top_products:
            clean_products.append({
                "product_name": p.get("product_name"),
                "price": p.get("price"),
                "currency": p.get("currency"),
                "canonical_id": p.get("canonical_id")
            })
        
        # 3. Knowledge
        kg_context = self.knowledge.explain(category)
        
        # Parse the string response from explain()
        knowledge_data = {}
        if "I'm sorry" not in kg_context:
            parts = kg_context.split("\n\nRelated Concepts: ")
            knowledge_data = {
                "definition": parts[0].strip(),
                "related_styles": parts[1].split(", ") if len(parts) > 1 else []
            }
        
        # 4. Assemble
        return {
            "category": category,
            "confidence": confidence,
            "style": inferred_style,
            "metal": inferred_metal,
            "similar_products": clean_products,
            "knowledge": knowledge_data
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORNEXA Copilot v1")
    parser.add_argument("--image", type=str, required=True, help="Path to jewelry image")
    args = parser.parse_args()
    
    # Run from root dir perspective
    copilot = OrnexaCopilot(
        weights_path="runs/classify/runs/ornexa_vision/weights/best.pt",
        data_dir="ingestion/processed_data"
    )
    
    result = copilot.analyze_image(args.image)
    print("\n=======================================")
    print("        ORNEXA COPILOT RESPONSE        ")
    print("=======================================")
    print(json.dumps(result, indent=4))
    print("=======================================\n")
