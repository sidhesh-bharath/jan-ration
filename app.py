from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="JanRation demo",
    description="A synthetic, non-official PDS citizen experience for hackathon testing.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class EntitlementRequest(BaseModel):
    card_reference: str = Field(min_length=3, max_length=32)


class GrievanceRequest(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=10, max_length=500)
    contact: Optional[str] = Field(default=None, max_length=80)


DEMO_ENTITLEMENT = {
    "card_reference": "DEMO-7824",
    "masked_household": "S. Kumar household",
    "state": "Tamil Nadu",
    "district": "Chennai",
    "category": "Priority Household (PHH)",
    "last_updated": "27 Aug 2026",
    "items": [
        {"name": "Rice", "quantity": "20 kg", "price": "₹0 / kg"},
        {"name": "Wheat", "quantity": "5 kg", "price": "₹0 / kg"},
        {"name": "Toor dal", "quantity": "1 kg", "price": "₹30 / kg"},
    ],
    "next_distribution": "1–30 Sep 2026",
    "shop_reference": "TN-CHN-1042",
    "source": "Tamil Nadu adapter (synthetic)",
    "source_status": "Live demo record",
}

SHOPS = [
    {
        "name": "Sri Murugan Fair Price Shop",
        "reference": "TN-CHN-1042",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "address": "18, Lake View Road, Velachery",
        "distance": "0.8 km",
        "hours": "8:00–13:00 · 16:00–18:00",
        "status": "Open today",
        "stock_note": "Rice and wheat reported available",
        "stock_updated": "Today, 08:40",
        "queue_minutes": 12,
        "wheelchair_accessible": True,
        "onorc_enabled": True,
    },
    {
        "name": "Makkal Sevai PDS Centre",
        "reference": "TN-CHN-1097",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "address": "4, Gandhi Street, Guindy",
        "distance": "2.1 km",
        "hours": "9:00–13:00 · 15:00–18:00",
        "status": "Open today",
        "stock_note": "All listed items reported available",
        "stock_updated": "Today, 09:05",
        "queue_minutes": 24,
        "wheelchair_accessible": False,
        "onorc_enabled": True,
    },
    {
        "name": "Jan Aahar Centre",
        "reference": "MH-PUN-2408",
        "state": "Maharashtra",
        "district": "Pune",
        "address": "11, Market Yard Road, Pune",
        "distance": "1.4 km",
        "hours": "9:00–17:00",
        "status": "Open today",
        "stock_note": "Rice and dal reported available",
        "stock_updated": "Yesterday, 16:20",
        "queue_minutes": 8,
        "wheelchair_accessible": True,
        "onorc_enabled": False,
    },
]

STATE_ADAPTERS = [
    {"code": "TN", "name": "Tamil Nadu", "adapter": "tnpds", "status": "demo-ready"},
    {"code": "MH", "name": "Maharashtra", "adapter": "mahafood", "status": "demo-ready"},
    {"code": "JK", "name": "Jammu and Kashmir", "adapter": "aepds-jk", "status": "planned"},
]


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "demo",
        "message": "JanRation API is ready",
        "data_policy": "synthetic-only",
    }


@app.get("/api/states")
def states() -> dict:
    """Expose the common adapter contract used by the unified front door."""
    return {"count": len(STATE_ADAPTERS), "states": STATE_ADAPTERS}


@app.get("/api/portability")
def portability(home_state: str = Query(..., min_length=2), current_state: str = Query(..., min_length=2)) -> dict:
    """Return synthetic ONORC guidance without contacting a live PDS system."""
    same_state = home_state.strip().lower() == current_state.strip().lower()
    return {
        "eligible": True,
        "home_state": home_state.strip(),
        "current_state": current_state.strip(),
        "message": (
            "You can use your home-state entitlement at an ONORC-enabled shop here."
            if not same_state
            else "You can collect from a nearby shop in your home state."
        ),
        "steps": [
            "Take your ration card or state-approved reference.",
            "Ask for an ONORC-enabled Fair Price Shop.",
            "Check the quantity shown before confirming the lift.",
        ],
        "shop_reference": "TN-CHN-1042" if not same_state else DEMO_ENTITLEMENT["shop_reference"],
    }


@app.post("/api/entitlement")
def entitlement(payload: EntitlementRequest) -> dict:
    """Return synthetic data for the demo reference only.

    Production should use a consented state adapter and never log raw identifiers.
    """
    reference = payload.card_reference.strip().upper()
    if reference not in {"DEMO-7824", "DEMO7824"}:
        return {
            "found": False,
            "message": "For this prototype, use the demo reference DEMO-7824. No real card data is connected.",
        }
    return {"found": True, "data": DEMO_ENTITLEMENT}


@app.get("/api/shops")
def shops(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
) -> dict:
    matches = SHOPS
    if state:
        matches = [shop for shop in matches if shop["state"].lower() == state.lower()]
    if district:
        matches = [shop for shop in matches if shop["district"].lower() == district.lower()]
    return {"count": len(matches), "shops": matches}


@app.post("/api/grievances")
def create_grievance(payload: GrievanceRequest) -> dict[str, str]:
    ticket = f"JR-{uuid4().hex[:6].upper()}"
    return {
        "ticket": ticket,
        "status": "Submitted",
        "message": "Your demo complaint has been recorded. Save this ticket reference to track it.",
    }
