from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/rates", tags=["Rates"])

# In-memory rates database (INR per gram)
global_rates = {
    "24K Gold": 7200,
    "22K Gold": 6800,
    "18K Gold": 5500,
    "Platinum": 3800,
    "Silver": 95
}

class UpdateRatesRequest(BaseModel):
    rates: dict

@router.get("")
async def get_rates():
    """Get the current global metal rates."""
    return global_rates

@router.post("")
async def update_rates(request: UpdateRatesRequest):
    """Update the global metal rates."""
    for key, value in request.rates.items():
        if key in global_rates:
            global_rates[key] = value
    return global_rates
