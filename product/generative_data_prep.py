import os
import zipfile
import json
import random
from PIL import Image

def extract_and_prepare_micro_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_zip = os.path.join(base_dir, "dataset.zip")
    archive_zip = os.path.join(base_dir, "archive.zip")
    
    raw_dir = os.path.join(base_dir, "data", "raw_images")
    lora_dir = os.path.join(base_dir, "data", "lora_training", "train")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(lora_dir, exist_ok=True)

    print("[DataPrep] Step 1: Unzipping dataset.zip (Partial Extract for Micro-dataset)")
    # Instead of unzipping all 405MB, we just extract ~150 bracelet images directly from the zip to save time & disk space
    bracelet_images = []
    with zipfile.ZipFile(dataset_zip, 'r') as z:
        for info in z.infolist():
            if "dataset/bracelet/" in info.filename and not info.filename.endswith('/'):
                bracelet_images.append(info.filename)
                
        # Select 100 random images for the micro-dataset
        selected = random.sample(bracelet_images, min(100, len(bracelet_images)))
        
        print(f"[DataPrep] Selected {len(selected)} images for the micro-dataset.")
        
        for file in selected:
            z.extract(file, raw_dir)

    print("[DataPrep] Step 2: Processing Images & Generating Captions")
    metadata = []
    
    extracted_bracelet_dir = os.path.join(raw_dir, "dataset", "bracelet")
    if os.path.exists(extracted_bracelet_dir):
        for idx, filename in enumerate(os.listdir(extracted_bracelet_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(extracted_bracelet_dir, filename)
                try:
                    # SD1.5 requires 512x512 images
                    with Image.open(img_path) as img:
                        # Convert to RGB to drop alpha channels if any
                        img = img.convert('RGB')
                        # Simple resize (in production, we'd crop/pad to preserve aspect ratio)
                        img = img.resize((512, 512), Image.Resampling.LANCZOS)
                        
                        out_filename = f"bangle_{idx:04d}.jpg"
                        out_path = os.path.join(lora_dir, out_filename)
                        img.save(out_path, format="JPEG", quality=90)
                        
                        # Generate the caption (we use 'sks' as a rare token identifier if we were doing Dreambooth, 
                        # but for standard LoRA we just describe it)
                        caption = f"A highly detailed, intricate gold jewelry bracelet, professional photography, white background"
                        
                        metadata.append({
                            "file_name": out_filename,
                            "text": caption
                        })
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")

    print("[DataPrep] Step 3: Writing metadata.jsonl")
    with open(os.path.join(lora_dir, "metadata.jsonl"), 'w') as f:
        for entry in metadata:
            f.write(json.dumps(entry) + '\n')
            
    print(f"[DataPrep] Complete! Processed {len(metadata)} images into {lora_dir}.")

if __name__ == "__main__":
    extract_and_prepare_micro_dataset()
