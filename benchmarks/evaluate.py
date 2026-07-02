import json
import os
import sys

# Add product/ to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "product"))

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ingestion"))

from query_engine import OrnexaQueryEngine
from knowledge_explorer import OrnexaKnowledgeExplorer
from vision_classifier import OrnexaVisionClassifier, ULTRALYTICS_AVAILABLE
from taxonomy import enhance_taxonomy

def run_search_benchmarks():
    try:
        with open("search_queries.json", "r") as f:
            benchmarks = json.load(f)
    except Exception as e:
        print(f"Error loading search_queries.json: {e}")
        return 0.0

    engine = OrnexaQueryEngine("../ingestion/processed_data")
    passed = 0
    total = len(benchmarks)

    for b in benchmarks:
        query = b["query"]
        results = engine.search(**query)
        
        result_ids = [r.get("canonical_id") for r in results]
        expected_ids = b.get("expected_ids", [])
        
        # Check if min results met
        min_met = len(results) >= b.get("expected_min_results", 0)
        # Check if expected IDs are in results
        ids_met = all(eid in result_ids for eid in expected_ids)
        
        if min_met and ids_met:
            passed += 1

    return passed / total if total > 0 else 0.0

def run_knowledge_benchmarks():
    try:
        with open("jewelry_questions.json", "r") as f:
            benchmarks = json.load(f)
    except Exception as e:
        print(f"Error loading jewelry_questions.json: {e}")
        return 0.0

    explorer = OrnexaKnowledgeExplorer()
    passed = 0
    total = len(benchmarks)

    for b in benchmarks:
        question = b["question"]
        expected_keywords = b.get("expected_keywords", [])
        
        response = explorer.explain(question).lower()
        
        # Check if all keywords are in response
        if all(kw.lower() in response for kw in expected_keywords):
            passed += 1

    return passed / total if total > 0 else 0.0

def run_taxonomy_benchmarks():
    try:
        with open("taxonomy_queries.json", "r") as f:
            benchmarks = json.load(f)
    except Exception as e:
        print(f"Error loading taxonomy_queries.json: {e}")
        return 0.0

    passed = 0
    total = len(benchmarks)

    for b in benchmarks:
        desc = b["description"]
        expected = b["expected"]
        
        mapped_data = {"description": desc}
        enhanced = enhance_taxonomy(mapped_data)
        
        match = True
        for key, expected_val in expected.items():
            actual_val = enhanced.get(key)
            if isinstance(expected_val, list):
                if not actual_val or not all(v in actual_val for v in expected_val):
                    match = False
                    break
            else:
                if str(actual_val) != str(expected_val):
                    match = False
                    break
                    
        if match:
            passed += 1

    return passed / total if total > 0 else 0.0

def run_classification_benchmarks():
    try:
        with open("vision_scores.json", "r") as f:
            scores = json.load(f)
            return scores.get("classification_accuracy", 0.0)
    except Exception as e:
        print(f"Error loading vision_scores.json: {e}")
        return 0.0

if __name__ == "__main__":
    print("=======================================")
    print("    ORNEXA FOUNDER VALIDATION SPRINT   ")
    print("=======================================\n")
    
    print("Running Search Benchmarks...")
    search_score = run_search_benchmarks()
    
    print("Running Knowledge Benchmarks...")
    knowledge_score = run_knowledge_benchmarks()
    
    print("Running Taxonomy Benchmarks...")
    taxonomy_score = run_taxonomy_benchmarks()
    
    print("Running Classification Benchmarks...")
    classification_score = run_classification_benchmarks()
    
    scorecard = {
        "search_accuracy": round(search_score, 2),
        "taxonomy_accuracy": round(taxonomy_score, 2),
        "knowledge_accuracy": round(knowledge_score, 2),
        "classification_accuracy": round(classification_score, 2)
    }
    
    # Calculate Overall
    overall = sum(scorecard.values()) / 4.0
    scorecard["overall"] = round(overall, 2)
    
    print("\n=======================================")
    print("           FINAL SCORECARD             ")
    print("=======================================")
    print(json.dumps(scorecard, indent=4))
    
    with open("scorecard.json", "w") as f:
        json.dump(scorecard, f, indent=4)
        
    print("\nSaved to benchmarks/scorecard.json")
