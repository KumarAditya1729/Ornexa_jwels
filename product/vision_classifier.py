import argparse
import os

# Try to import ultralytics, but don't fail if it's not installed yet.
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class OrnexaVisionClassifier:
    def __init__(self, model_weights="yolov8n-cls.pt"):
        """
        Initializes the YOLO classifier.
        Defaults to YOLOv8 nano classification model. 
        Once custom weights are trained, pass 'best.pt' here.
        """
        self.model_weights = model_weights
        if ULTRALYTICS_AVAILABLE:
            # We initialize the model. If weights don't exist, it downloads the base model.
            self.model = YOLO(self.model_weights)
        else:
            self.model = None

    def train(self, data_yaml_path, epochs=10):
        """
        Trains the YOLO model on the provided dataset.
        """
        if not ULTRALYTICS_AVAILABLE:
            return "Error: 'ultralytics' package is not installed. Run: pip install ultralytics"
            
        if not os.path.exists(data_yaml_path):
            return f"Error: Dataset yaml not found at {data_yaml_path}"
            
        print(f"[VisionClassifier] Starting training on {data_yaml_path} for {epochs} epochs...")
        results = self.model.train(data=data_yaml_path, epochs=epochs, imgsz=224)
        return f"Training completed. Weights saved in runs/classify/train/weights/"

    def classify(self, image_path):
        """
        Classifies a given image.
        """
        if not ULTRALYTICS_AVAILABLE:
            return "Error: 'ultralytics' package is not installed. Run: pip install ultralytics"
            
        if not os.path.exists(image_path):
            return f"Error: Image not found at {image_path}"
            
        print(f"[VisionClassifier] Analyzing {image_path}...")
        results = self.model(image_path)
        
        # Parse top1 result
        probs = results[0].probs
        top1_index = probs.top1
        confidence = probs.top1conf.item()
        category_name = results[0].names[top1_index]
        
        return {
            "predicted_category": category_name,
            "confidence": round(confidence, 4)
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORNEXA Vision Classifier (YOLOv8)")
    parser.add_argument("--mode", choices=["train", "predict"], required=True, help="Mode to run")
    parser.add_argument("--data", type=str, help="Path to data.yaml (for training)")
    parser.add_argument("--image", type=str, help="Path to image (for prediction)")
    parser.add_argument("--weights", type=str, default="yolov8n-cls.pt", help="Path to model weights")
    
    args = parser.parse_args()
    
    classifier = OrnexaVisionClassifier(args.weights)
    
    if args.mode == "train":
        if not args.data:
            print("Error: --data is required for training mode.")
        else:
            print(classifier.train(args.data))
            
    elif args.mode == "predict":
        if not args.image:
            print("Error: --image is required for predict mode.")
        else:
            result = classifier.classify(args.image)
            print("\n--- Classification Result ---")
            if isinstance(result, dict):
                print(f"Category: {result['predicted_category']}")
                print(f"Confidence: {result['confidence']*100:.2f}%")
            else:
                print(result)
            print("-----------------------------\n")
