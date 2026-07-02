import torch
from diffusers import StableDiffusionPipeline
import os
import uuid

# Determine optimal device (MPS for Apple Silicon, CUDA for Nvidia, CPU as fallback)
if torch.backends.mps.is_available():
    device = "mps"
    dtype = torch.float16
elif torch.cuda.is_available():
    device = "cuda"
    dtype = torch.float16
else:
    device = "cpu"
    dtype = torch.float32

print(f"[Generative AI] Initializing Stable Diffusion on {device}...")

# We disable safety checker for speed and to prevent false positives on shiny jewelry shapes
model_id = "runwayml/stable-diffusion-v1-5"
try:
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype, safety_checker=None, requires_safety_checker=False)
    pipe = pipe.to(device)
    # Recommended for Apple Silicon (MPS) to reduce memory usage
    if device == "mps":
        pipe.enable_attention_slicing()
    MODEL_LOADED = True
except Exception as e:
    print(f"[Generative AI] Failed to load model: {e}")
    MODEL_LOADED = False

def generate_jewelry_sketch(prompt: str, output_dir: str = "../web/public/generations"):
    """
    Generates an image using local Stable Diffusion based on the prompt.
    Returns the URL/path to the saved image.
    """
    if not MODEL_LOADED:
        return "/mocks/sketch_1.png" # Fallback if model fails

    # Enhance the prompt to specifically target jewelry design sketches
    enhanced_prompt = f"high quality, intricate jewelry design sketch, {prompt}, isolated on white background, 8k resolution, photorealistic rendering, detailed craftsmanship"
    negative_prompt = "blurry, distorted, low quality, human, face, hands, messy, text, watermark"

    print(f"[Generative AI] Generating image for: '{prompt}'")
    
    # Generate image (using fewer steps for speed in the pilot demo)
    image = pipe(enhanced_prompt, negative_prompt=negative_prompt, num_inference_steps=25).images[0]

    # Save to disk
    os.makedirs(output_dir, exist_ok=True)
    filename = f"gen_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)
    image.save(filepath)
    
    print(f"[Generative AI] Image saved to {filepath}")
    
    # Return the relative path for the React frontend
    return f"/generations/{filename}"

if __name__ == "__main__":
    # Test script
    print("Testing local generation...")
    url = generate_jewelry_sketch("traditional polki bangles with rubies", output_dir="./test_outputs")
    print(f"Generated test URL: {url}")
