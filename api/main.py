import sys
import os
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil

# Ensure we can import from product
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product.copilot import OrnexaCopilot
from api.workflow import router as workflow_router
from api.rates import router as rates_router

app = FastAPI(
    title="ORNEXA Intelligence API",
    description="Production API for the ORNEXA Jewelry Intelligence System. Exposes Vision Classification, Commerce Search, Semantic Knowledge, and Copilot Pipelines.",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register workflow routes
app.include_router(workflow_router)
app.include_router(rates_router)

# Initialize master engines
copilot = OrnexaCopilot(
    weights_path="runs/classify/runs/ornexa_vision/weights/best.pt",
    data_dir="ingestion/processed_data"
)

os.makedirs("api/temp", exist_ok=True)

@app.get("/api/health", tags=["System"])
async def health_check():
    """System uptime and status check."""
    return {
        "status": "online", 
        "version": "1.0.0", 
        "models_loaded": True
    }

@app.post("/api/classify", tags=["Intelligence"])
async def classify_image(file: UploadFile = File(...)):
    """Exposes raw YOLOv8 vision classification without the Copilot commerce wrapper."""
    temp_path = f"api/temp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    result = copilot.vision.classify(temp_path)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return result

@app.post("/api/copilot", tags=["Intelligence"])
async def analyze_image(file: UploadFile = File(...)):
    """The unified end-to-end pipeline (Image -> Category -> Similar Products -> Knowledge)."""
    temp_path = f"api/temp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    result = copilot.analyze_image(temp_path)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return result

@app.get("/api/search", tags=["Commerce"])
async def search_catalog(category: str = None, metal: str = None, gemstone: str = None, style: str = None):
    """Direct catalog querying by metadata."""
    return copilot.search.search(category, metal, gemstone, style)

@app.get("/api/knowledge", tags=["Semantic Graph"])
async def explain_term(query: str):
    """Exposes the semantic jewelry graph for definitions and relationships."""
    return {"explanation": copilot.knowledge.explain(query)}

@app.get("/api/analytics", tags=["System"])
async def get_analytics():
    """Returns the live benchmark scorecard."""
    try:
        with open("benchmarks/scorecard.json", "r") as f:
            return json.load(f)
    except Exception:
        return {"error": "Scorecard not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
