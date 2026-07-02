from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import time
from typing import Optional
from api.rates import global_rates
import sys
import os

# Add the root directory to path so we can import from product
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from product.generative_vision import generate_jewelry_sketch
import uuid
import time
from typing import Optional

router = APIRouter(prefix="/api/order", tags=["Workflow"])

# In-memory database for demo
orders_db = {
    "ORD-1001": {
        "id": "ORD-1001", "status": "Casting", "requirement": "Heavy bridal Kundan set", "category": "Necklace",
        "sketches": [{"id": "s1", "url": "/mocks/sketch_1.png", "style": "Bridal"}], "version": 2, "approved_sketch": {"id": "s1", "url": "/mocks/sketch_1.png", "style": "Bridal"},
        "cad_url": "/mocks/model.glb", "approval_ledger": [], "bom": [{"component": "22K Gold", "qty": "120g"}],
        "notes": {"internal": "Priority order for VIP client.", "customer": "", "production": "Ensure strict weight tolerance."}, "attachments": [],
        "created_at": time.time() - 86400 * 3, "updated_at": time.time() - 3600
    },
    "ORD-1002": {
        "id": "ORD-1002", "status": "CAD Review", "requirement": "Modern geometric ruby ring", "category": "Ring",
        "sketches": [{"id": "s2", "url": "/mocks/sketch_2.png", "style": "Modern"}], "version": 1, "approved_sketch": {"id": "s2", "url": "/mocks/sketch_2.png", "style": "Modern"},
        "cad_url": "/mocks/model.glb", "approval_ledger": [], "bom": None,
        "notes": {"internal": "", "customer": "", "production": ""}, "attachments": [],
        "created_at": time.time() - 86400 * 1, "updated_at": time.time() - 7200
    },
    "ORD-1003": {
        "id": "ORD-1003", "status": "QC", "requirement": "Traditional Polki bangles", "category": "Bracelet",
        "sketches": [{"id": "s3", "url": "/mocks/sketch_1.png", "style": "Traditional"}], "version": 1, "approved_sketch": {"id": "s3", "url": "/mocks/sketch_1.png", "style": "Traditional"},
        "cad_url": "/mocks/model.glb", "approval_ledger": [], "bom": [{"component": "18K Gold", "qty": "40g"}],
        "notes": {"internal": "", "customer": "", "production": ""}, "attachments": [],
        "created_at": time.time() - 86400 * 5, "updated_at": time.time() - 1800
    },
    "ORD-1004": {
        "id": "ORD-1004", "status": "Requirement Received", "requirement": "Emerald pendant with diamond halo", "category": "Pendant",
        "sketches": [], "version": 1, "approved_sketch": None,
        "cad_url": None, "approval_ledger": [], "bom": None,
        "notes": {"internal": "", "customer": "", "production": ""}, "attachments": [],
        "created_at": time.time() - 3600, "updated_at": time.time() - 3600
    }
}

class OrderRequest(BaseModel):
    requirement: str
    category: str = "Unknown"

class FeedbackRequest(BaseModel):
    feedback: str

@router.get("s")
async def get_all_orders():
    """Returns all active custom orders."""
    # Convert dict to sorted list by updated_at descending
    all_orders = list(orders_db.values())
    all_orders.sort(key=lambda x: x["updated_at"], reverse=True)
    return all_orders

@router.post("/new")
async def create_order(request: OrderRequest):
    order_id = str(uuid.uuid4())[:8]
    orders_db[order_id] = {
        "id": order_id,
        "status": "Requirement Received",
        "requirement": request.requirement,
        "category": request.category,
        "sketches": [],
        "version": 1,
        "approved_sketch": None,
        "cad_url": None,
        "approval_ledger": [],
        "bom": None,
        "notes": {"internal": "", "customer": "", "production": ""},
        "attachments": [],
        "created_at": time.time(),
        "updated_at": time.time()
    }
    return orders_db[order_id]

class NoteRequest(BaseModel):
    type: str  # internal, customer, production
    content: str

@router.post("/{order_id}/notes")
async def add_note(order_id: str, request: NoteRequest):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    order["notes"][request.type] = request.content
    
    order["approval_ledger"].append({
        "action": f"Updated {request.type.capitalize()} Note",
        "remarks": request.content,
        "timestamp": time.time()
    })
    
    order["updated_at"] = time.time()
    return order

class AttachRequest(BaseModel):
    filename: str
    filetype: str

@router.post("/{order_id}/attach")
async def add_attachment(order_id: str, request: AttachRequest):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    order["attachments"].append({
        "filename": request.filename,
        "filetype": request.filetype,
        "uploaded_at": time.time()
    })
    
    order["approval_ledger"].append({
        "action": "File Attached",
        "remarks": request.filename,
        "timestamp": time.time()
    })
    
    order["updated_at"] = time.time()
    return order

@router.post("/{order_id}/generate_sketches")
async def generate_sketches(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    
    # Generate real image locally using MPS (Mac)
    requirement = order["requirement"]
    if order["version"] > 1:
        # Include feedback history for V2+
        feedback_history = " ".join([e["remarks"] for e in order["approval_ledger"] if e["action"] == "Feedback Submitted"])
        requirement = f"{requirement}, incorporating changes: {feedback_history}"
        
    # Generate the sketch
    # We output to the public web folder so React can serve it directly
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "public", "generations")
    image_url = generate_jewelry_sketch(requirement, output_dir=output_dir)
    
    if order["version"] == 1:
        order["sketches"] = [
            {"id": "sketch_1_v1", "url": image_url, "style": "AI Generated (v1)"}
        ]
    else:
        order["sketches"] = [
            {"id": f"sketch_1_v{order['version']}", "url": image_url, "style": f"AI Generated (v{order['version']})"}
        ]
        
    order["status"] = "Sketch Review"
    order["updated_at"] = time.time()
    return order

@router.post("/{order_id}/feedback")
async def submit_feedback(order_id: str, request: FeedbackRequest):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    
    # Log feedback and iterate version
    order["approval_ledger"].append({
        "action": "Feedback Submitted",
        "remarks": request.feedback,
        "version": order["version"],
        "timestamp": time.time()
    })
    
    order["version"] += 1
    order["status"] = "Generating Revision"
    order["updated_at"] = time.time()
    return order

@router.post("/{order_id}/approve_sketch")
async def approve_sketch(order_id: str, sketch_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    sketch = next((s for s in order["sketches"] if s["id"] == sketch_id), None)
    if not sketch:
        raise HTTPException(status_code=404, detail="Sketch not found")
        
    order["approved_sketch"] = sketch
    order["status"] = "Sketch Approved"
    
    # Add to immutable ledger
    order["approval_ledger"].append({
        "action": "Sketch Approved",
        "approved_by": "Customer",
        "version": order["version"],
        "asset": sketch["url"],
        "timestamp": time.time()
    })
    
    order["updated_at"] = time.time()
    return order

@router.post("/{order_id}/generate_cad")
async def generate_cad(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    time.sleep(2.0)
    
    order["cad_url"] = "/mocks/model.glb"
    order["status"] = "CAD Review"
    order["updated_at"] = time.time()
    return order

@router.post("/{order_id}/approve_cad")
async def approve_cad(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    order["status"] = "CAD Approved"
    
    # Add to ledger
    order["approval_ledger"].append({
        "action": "CAD Approved",
        "approved_by": "Production Manager",
        "version": order["version"],
        "asset": order["cad_url"],
        "timestamp": time.time()
    })
    
    # Auto-generate BOM upon CAD approval
    order["bom"] = [
        {"component": "22K Gold", "qty": "45g", "type": "metal"},
        {"component": "Ruby", "qty": "24 pcs", "type": "stone", "price_per_unit": 1200},
        {"component": "Pearl", "qty": "16 pcs", "type": "stone", "price_per_unit": 500}
    ]
    
    # Calculate initial costing
    gold_weight = 45 # grams
    gold_rate = global_rates.get("22K Gold", 6800)
    material_cost = gold_weight * gold_rate
    stone_cost = (24 * 1200) + (16 * 500)
    making_cost = 22000
    cad_cost = 3000
    total_cost = material_cost + stone_cost + making_cost + cad_cost
    
    order["costing"] = {
        "material_cost": material_cost,
        "stone_cost": stone_cost,
        "making_cost": making_cost,
        "cad_cost": cad_cost,
        "total_cost": total_cost,
        "margin_percent": 25,
        "selling_price": int(total_cost * 1.25)
    }
    
    order["updated_at"] = time.time()
    return order

class MarginRequest(BaseModel):
    margin_percent: int

@router.post("/{order_id}/update_margin")
async def update_margin(order_id: str, request: MarginRequest):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    if "costing" not in order:
        raise HTTPException(status_code=400, detail="Costing not calculated yet")
        
    order["costing"]["margin_percent"] = request.margin_percent
    order["costing"]["selling_price"] = int(order["costing"]["total_cost"] * (1 + request.margin_percent / 100.0))
    order["updated_at"] = time.time()
    return order

@router.get("/{order_id}/work_order")
async def generate_work_order(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    order["status"] = "Work Order Created"
    order["updated_at"] = time.time()
    return order

@router.post("/{order_id}/manufacturing_state")
async def update_manufacturing_state(order_id: str, state: str):
    """Moves order through physical stages: Production Released -> Casting -> Assembly -> QC -> Dispatch"""
    valid_states = ["Production Released", "Casting", "Assembly", "Stone Setting", "Polishing", "QC", "Ready Dispatch"]
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    if state not in valid_states:
        raise HTTPException(status_code=400, detail="Invalid manufacturing state")
        
    order = orders_db[order_id]
    order["status"] = state
    
    order["approval_ledger"].append({
        "action": f"Moved to {state}",
        "approved_by": "Factory Floor",
        "timestamp": time.time()
    })
    
    order["updated_at"] = time.time()
    return order

@router.get("/{order_id}")
async def get_order(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]
