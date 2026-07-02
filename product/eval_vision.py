import os
import json
from ultralytics import YOLO

def main():
    benchmark_dir = "/Users/adityashrivastava/Desktop/ORNEXA JEWLS/benchmarks/classification_test_set"
    expected_answers_path = "/Users/adityashrivastava/Desktop/ORNEXA JEWLS/benchmarks/expected_answers.json"
    
    print("\n--- Evaluating on Locked Benchmark Set ---")
    with open(expected_answers_path, "r") as f:
        expected = json.load(f)
        
    correct = 0
    total = 0
    
    classes = ["Ring", "Necklace", "Earring", "Bracelet", "Pendant"]
    conf_matrix = {c: {p: 0 for p in classes} for c in classes}
    
    # Load the best model that was just trained
    # Path extracted from Ultralytics train log
    best_model = YOLO("/Users/adityashrivastava/Desktop/ORNEXA JEWLS/runs/classify/runs/ornexa_vision/weights/best.pt")
    
    for item in expected:
        img_path = os.path.join(benchmark_dir, item["image"])
        if not os.path.exists(img_path):
            continue
            
        true_cat = item["expected_category"]
        total += 1
        
        # Predict
        res = best_model(img_path, verbose=False)[0]
        pred_idx = res.probs.top1
        pred_cat = res.names[pred_idx]
        
        if pred_cat == true_cat:
            correct += 1
            
        if true_cat in conf_matrix and pred_cat in conf_matrix[true_cat]:
            conf_matrix[true_cat][pred_cat] += 1
            
    accuracy = correct / total if total > 0 else 0
    
    print("\n=== CLASSIFICATION BENCHMARK RESULTS ===")
    print(f"Top-1 Accuracy: {accuracy:.2%}")
    print("\nConfusion Matrix (Rows: True, Cols: Predicted):")
    
    print(f"{'':>10}" + "".join([f"{c[:4]:>8}" for c in classes]))
    for true_c in classes:
        row = [f"{conf_matrix[true_c][pred_c]:>8}" for pred_c in classes]
        print(f"{true_c[:10]:>10}" + "".join(row))
        
    # Save scores to be read by evaluate.py
    vision_scores = {
        "classification_accuracy": accuracy,
        "confusion_matrix": conf_matrix
    }
    with open("/Users/adityashrivastava/Desktop/ORNEXA JEWLS/benchmarks/vision_scores.json", "w") as f:
        json.dump(vision_scores, f, indent=4)
        
    print("\nSaved vision_scores.json!")

if __name__ == "__main__":
    main()
