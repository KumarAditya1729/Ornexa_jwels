import os
import glob
import random
import shutil
import json
from PIL import Image

SOURCE_DIR = "/Users/adityashrivastava/Desktop/ORNEXA JEWLS/ingestion/processed_data/extracted_jewellery classifier.v1i.yolov8"
OUTPUT_DIR = "/Users/adityashrivastava/Desktop/ORNEXA JEWLS/dataset_cls"
BENCHMARK_DIR = "/Users/adityashrivastava/Desktop/ORNEXA JEWLS/benchmarks/classification_test_set"
EXPECTED_ANSWERS_PATH = "/Users/adityashrivastava/Desktop/ORNEXA JEWLS/benchmarks/expected_answers.json"

# Mapping YOLO detection class indices to target classification strings
CLASS_MAP = {
    2: "Bracelet",   # BANGLE
    3: "Bracelet",   # BRACELET
    4: "Necklace",   # CHAIN
    5: "Earring",    # EAR WEAR
    6: "Ring",       # FINGER RING
    7: "Necklace",   # NECKLACE
    9: "Pendant"     # Pendant
}

def parse_yolo_label(txt_path):
    boxes = []
    if not os.path.exists(txt_path):
        return boxes
    with open(txt_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                if class_id in CLASS_MAP:
                    boxes.append({
                        "class_name": CLASS_MAP[class_id],
                        "cx": float(parts[1]),
                        "cy": float(parts[2]),
                        "w": float(parts[3]),
                        "h": float(parts[4])
                    })
    return boxes

def crop_and_save(img_path, box, out_path):
    try:
        with Image.open(img_path) as img:
            img_w, img_h = img.size
            cx, cy = box['cx'] * img_w, box['cy'] * img_h
            w, h = box['w'] * img_w, box['h'] * img_h
            
            left = max(0, cx - w/2)
            top = max(0, cy - h/2)
            right = min(img_w, cx + w/2)
            bottom = min(img_h, cy + h/2)
            
            cropped = img.crop((left, top, right, bottom))
            # Convert to RGB if RGBA
            if cropped.mode in ('RGBA', 'P'):
                cropped = cropped.convert('RGB')
            cropped.save(out_path, format="JPEG")
    except Exception as e:
        print(f"Error cropping {img_path}: {e}")

def main():
    # 1. Collect all valid crops
    print("Parsing dataset...")
    all_crops = {c: [] for c in set(CLASS_MAP.values())}
    
    # We will search train, valid, test folders
    for split in ["train", "valid", "test"]:
        img_dir = os.path.join(SOURCE_DIR, split, "images")
        lbl_dir = os.path.join(SOURCE_DIR, split, "labels")
        if not os.path.exists(img_dir): continue
        
        for img_path in glob.glob(os.path.join(img_dir, "*.*")):
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            txt_path = os.path.join(lbl_dir, base_name + ".txt")
            
            boxes = parse_yolo_label(txt_path)
            for idx, box in enumerate(boxes):
                all_crops[box['class_name']].append({
                    "src_img": img_path,
                    "box": box,
                    "out_name": f"{split}_{base_name}_{idx}.jpg"
                })

    # 2. Extract benchmark test set (10 per class)
    os.makedirs(BENCHMARK_DIR, exist_ok=True)
    benchmark_answers = []
    
    train_val_pool = {c: [] for c in all_crops}
    
    print("Extracting benchmark set...")
    for c, items in all_crops.items():
        random.shuffle(items)
        
        # Take up to 20 for benchmark
        test_count = min(20, len(items))
        test_items = items[:test_count]
        train_val_pool[c] = items[test_count:]
        
        for item in test_items:
            out_path = os.path.join(BENCHMARK_DIR, item['out_name'])
            crop_and_save(item['src_img'], item['box'], out_path)
            benchmark_answers.append({
                "image": item['out_name'],
                "expected_category": c
            })

    # Save expected answers
    with open(EXPECTED_ANSWERS_PATH, 'w') as f:
        json.dump(benchmark_answers, f, indent=4)
        
    print(f"Saved {len(benchmark_answers)} locked benchmark images.")

    # 3. Save Train/Val split (80/20)
    print("Creating train/val dataset...")
    for c, items in train_val_pool.items():
        random.shuffle(items)
        split_idx = int(len(items) * 0.8)
        
        train_items = items[:split_idx]
        val_items = items[split_idx:]
        
        # Train
        train_dir = os.path.join(OUTPUT_DIR, "train", c)
        os.makedirs(train_dir, exist_ok=True)
        for item in train_items:
            crop_and_save(item['src_img'], item['box'], os.path.join(train_dir, item['out_name']))
            
        # Val
        val_dir = os.path.join(OUTPUT_DIR, "val", c)
        os.makedirs(val_dir, exist_ok=True)
        for item in val_items:
            crop_and_save(item['src_img'], item['box'], os.path.join(val_dir, item['out_name']))
            
        print(f"{c}: {len(train_items)} train, {len(val_items)} val")

    # 4. Generate Dataset Audit Report
    audit_report = {}
    
    for c in CLASS_MAP.values():
        if c not in audit_report:
            audit_report[c] = {"train": 0, "val": 0, "test": 0}
            
    for item in benchmark_answers:
        audit_report[item["expected_category"]]["test"] += 1
        
    for split in ["train", "val"]:
        split_dir = os.path.join(OUTPUT_DIR, split)
        if os.path.exists(split_dir):
            for class_dir in os.listdir(split_dir):
                if class_dir in audit_report:
                    class_path = os.path.join(split_dir, class_dir)
                    audit_report[class_dir][split] = len(os.listdir(class_path))

    with open("dataset_audit.json", "w") as f:
        json.dump(audit_report, f, indent=4)
        
    print("\nDataset Audit Report:")
    print(json.dumps(audit_report, indent=4))
    print(f"\nDataset successfully remapped to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
