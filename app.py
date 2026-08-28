from copy import deepcopy
import os
from pathlib import Path
from time import time
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="JanRation API",
    description=(
        "A synthetic India Stack-aligned service contract for ration cardholder journeys, "
        "Fair Price Shops, and POS terminals. This is not an official government service."
    ),
    version="0.2.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class OTPRequest(BaseModel):
    card_reference: str = Field(min_length=3, max_length=32)


class OTPVerifyRequest(BaseModel):
    challenge_id: str = Field(min_length=8, max_length=64)
    otp: str = Field(pattern=r"^\d{6}$")


class ComplaintCreate(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=10, max_length=500)
    store_reference: Optional[str] = Field(default=None, max_length=32)


class TransactionItem(BaseModel):
    name: str = Field(min_length=2, max_length=40)
    quantity: float = Field(gt=0, le=100)
    unit: str = Field(default="kg", min_length=1, max_length=8)


class TransactionCreate(BaseModel):
    shop_reference: str = Field(min_length=4, max_length=32)
    terminal_reference: str = Field(min_length=4, max_length=48)
    card_reference: str = Field(min_length=3, max_length=32)
    idempotency_key: str = Field(min_length=8, max_length=80)
    items: list[TransactionItem] = Field(min_length=1, max_length=10)


class StockWebhook(BaseModel):
    shop_reference: str = Field(min_length=4, max_length=32)
    idempotency_key: str = Field(min_length=8, max_length=80)
    reported_at: str = Field(min_length=10, max_length=40)
    inventory: list[dict[str, str]] = Field(min_length=1, max_length=20)


DEMO_OTP = "246810"

# Deliberately synthetic. These records are the single source used by the demo UI and API.
DEMO_PROFILE = {
    "card_reference": "DEMO-7824",
    "masked_household": "Kumar household",
    "state": "Tamil Nadu",
    "district": "Chennai",
    "category": "Priority Household (PHH)",
    "member_count": 4,
    "card_status": "Active",
    "last_updated": "27 Aug 2026, 09:12 IST",
    "next_collection": "1–30 Sep 2026",
    "home_shop_reference": "TN-CHN-1042",
    "source": "Tamil Nadu adapter · synthetic read model",
    "allocations": [
        {"name": "Rice", "key": "rice", "total": 20, "withdrawn": 12, "remaining": 8, "unit": "kg", "price": "₹0 / kg", "color": "saffron"},
        {"name": "Wheat", "key": "wheat", "total": 5, "withdrawn": 2, "remaining": 3, "unit": "kg", "price": "₹0 / kg", "color": "leaf"},
        {"name": "Toor dal", "key": "dal", "total": 1, "withdrawn": 0.5, "remaining": 0.5, "unit": "kg", "price": "₹30 / kg", "color": "coral"},
        {"name": "Sugar", "key": "sugar", "total": 2, "withdrawn": 1, "remaining": 1, "unit": "kg", "price": "₹25 / kg", "color": "blue"},
    ],
    "transactions": [
        {"date": "12 Aug 2026", "shop": "Sri Murugan Fair Price Shop", "reference": "TXN-TN-8012", "items": "8 kg rice · 0.5 kg dal", "status": "Completed"},
        {"date": "18 Jul 2026", "shop": "Sri Murugan Fair Price Shop", "reference": "TXN-TN-7771", "items": "10 kg rice · 2 kg wheat", "status": "Completed"},
        {"date": "20 Jun 2026", "shop": "Makkal Sevai PDS Centre", "reference": "TXN-TN-7420", "items": "2 kg sugar · 1 kg dal", "status": "Completed"},
        {"date": "08 May 2026", "shop": "Sri Murugan Fair Price Shop", "reference": "TXN-TN-7199", "items": "20 kg rice · 5 kg wheat", "status": "Completed"},
        {"date": "11 Apr 2026", "shop": "Sri Murugan Fair Price Shop", "reference": "TXN-TN-6804", "items": "Authentication retry · no deduction", "status": "No deduction"},
    ],
    "notices": [
        {"type": "info", "title": "Your September window is open", "text": "You can collect from 1–30 Sep 2026 at an enabled Fair Price Shop."},
        {"type": "tip", "title": "Check before you confirm", "text": "The POS screen should show the quantity and price before a lift is completed."},
    ],
}

SHOPS = [
    {"id": "tn-1042", "name": "Sri Murugan Fair Price Shop", "reference": "TN-CHN-1042", "state": "Tamil Nadu", "district": "Chennai", "address": "18, Lake View Road, Velachery", "distance": "0.8 km", "hours": "8:00–13:00 · 16:00–18:00", "status": "Open today", "stock_note": "Rice, wheat and dal reported available", "stock_updated": "Today, 08:40", "queue_minutes": 12, "wheelchair_accessible": True, "onorc_enabled": True, "map_x": 39, "map_y": 42, "inventory": [{"name": "Rice", "available": "High"}, {"name": "Wheat", "available": "High"}, {"name": "Toor dal", "available": "Medium"}]},
    {"id": "tn-1097", "name": "Makkal Sevai PDS Centre", "reference": "TN-CHN-1097", "state": "Tamil Nadu", "district": "Chennai", "address": "4, Gandhi Street, Guindy", "distance": "2.1 km", "hours": "9:00–13:00 · 15:00–18:00", "status": "Open today", "stock_note": "All listed items reported available", "stock_updated": "Today, 09:05", "queue_minutes": 24, "wheelchair_accessible": False, "onorc_enabled": True, "map_x": 67, "map_y": 31, "inventory": [{"name": "Rice", "available": "High"}, {"name": "Wheat", "available": "Medium"}, {"name": "Toor dal", "available": "High"}]},
    {"id": "mh-2408", "name": "Jan Aahar Centre", "reference": "MH-PUN-2408", "state": "Maharashtra", "district": "Pune", "address": "11, Market Yard Road, Pune", "distance": "1.4 km", "hours": "9:00–17:00", "status": "Open today", "stock_note": "Rice and dal reported available", "stock_updated": "Yesterday, 16:20", "queue_minutes": 8, "wheelchair_accessible": True, "onorc_enabled": True, "map_x": 43, "map_y": 54, "inventory": [{"name": "Rice", "available": "High"}, {"name": "Wheat", "available": "Low"}, {"name": "Toor dal", "available": "High"}]},
    {"id": "jk-3001", "name": "Himalayan Public Distribution Point", "reference": "JK-SGR-3001", "state": "Jammu and Kashmir", "district": "Srinagar", "address": "12, Residency Road, Srinagar", "distance": "0.6 km", "hours": "9:30–16:30", "status": "Open today", "stock_note": "Rice and wheat reported available", "stock_updated": "Today, 07:55", "queue_minutes": 16, "wheelchair_accessible": True, "onorc_enabled": True, "map_x": 58, "map_y": 38, "inventory": [{"name": "Rice", "available": "High"}, {"name": "Wheat", "available": "High"}, {"name": "Toor dal", "available": "Low"}]},
    {"id": "ka-4402", "name": "Namma Anna Store", "reference": "KA-BLR-4402", "state": "Karnataka", "district": "Bengaluru Urban", "address": "22, 5th Main Road, Jayanagar", "distance": "1.8 km", "hours": "8:30–17:30", "status": "Open today", "stock_note": "Rice and sugar reported available", "stock_updated": "Today, 08:15", "queue_minutes": 10, "wheelchair_accessible": False, "onorc_enabled": True, "map_x": 29, "map_y": 62, "inventory": [{"name": "Rice", "available": "High"}, {"name": "Wheat", "available": "Medium"}, {"name": "Sugar", "available": "High"}]},
    {"id": "wb-5188", "name": "Bengal Jan Sahayata Kendra", "reference": "WB-KOL-5188", "state": "West Bengal", "district": "Kolkata", "address": "7, Canal South Road, Kolkata", "distance": "2.6 km", "hours": "10:00–18:00", "status": "Opening soon", "stock_note": "Last stock report: rice available", "stock_updated": "Yesterday, 14:10", "queue_minutes": 30, "wheelchair_accessible": True, "onorc_enabled": False, "map_x": 73, "map_y": 60, "inventory": [{"name": "Rice", "available": "Medium"}, {"name": "Wheat", "available": "Low"}, {"name": "Toor dal", "available": "Low"}]},
]

COMPLAINTS = [
    {"ticket": "JR-4A91C2", "category": "Quantity was incorrect", "shop": "Sri Murugan Fair Price Shop", "created": "14 Aug 2026", "status": "Under review", "status_key": "review", "update": "District office requested the POS receipt. Next update by 30 Aug."},
    {"ticket": "JR-19D8F0", "category": "Shop was closed", "shop": "Makkal Sevai PDS Centre", "created": "22 Jul 2026", "status": "Resolved", "status_key": "resolved", "update": "Opening hours were updated. Thank you for reporting this."},
    {"ticket": "JR-8C207B", "category": "Authentication failed", "shop": "Sri Murugan Fair Price Shop", "created": "08 Jun 2026", "status": "Closed", "status_key": "closed", "update": "A retry was recorded with no deduction from your entitlement."},
]

INITIAL_COMPLAINTS = deepcopy(COMPLAINTS)

STATE_ADAPTERS = [
    {"code": "TN", "name": "Tamil Nadu", "adapter": "tnpds", "status": "demo-ready", "last_sync": "09:12 IST"},
    {"code": "MH", "name": "Maharashtra", "adapter": "mahafood", "status": "demo-ready", "last_sync": "09:08 IST"},
    {"code": "JK", "name": "Jammu and Kashmir", "adapter": "aepds-jk", "status": "contract-ready", "last_sync": "08:57 IST"},
    {"code": "KA", "name": "Karnataka", "adapter": "ahara", "status": "contract-ready", "last_sync": "08:51 IST"},
    {"code": "WB", "name": "West Bengal", "adapter": "foodwb", "status": "contract-ready", "last_sync": "08:44 IST"},
]

otp_challenges: dict[str, dict] = {}
sessions: dict[str, dict] = {}
transaction_events: dict[str, dict] = {}
stock_events: dict[str, dict] = {}


def normalise_reference(reference: str) -> str:
    return reference.strip().upper().replace(" ", "")


def require_demo_session(authorization: Optional[str], session_token: Optional[str]) -> dict:
    token = session_token
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="A verified demo session is required for this resource.")
    return sessions[token]


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/developers", include_in_schema=False)
def developers() -> FileResponse:
    return FileResponse(STATIC_DIR / "developers.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "demo",
        "service": "JanRation API",
        "product": "JanRation",
        "data_policy": "synthetic-only",
    }


def require_shop_token(authorization: Optional[str]) -> None:
    if authorization != "Bearer demo-shop-token":
        raise HTTPException(status_code=401, detail="Use the synthetic shop token in the sandbox.")


@app.post("/api/transactions")
def record_transaction(payload: TransactionCreate, authorization: Optional[str] = Header(default=None)) -> dict:
    """Accept a synthetic ePoS lift event and make retries idempotent."""
    require_shop_token(authorization)
    if not any(shop["reference"] == payload.shop_reference for shop in SHOPS):
        raise HTTPException(status_code=404, detail="Unknown synthetic shop reference.")
    if payload.idempotency_key in transaction_events:
        return {"ok": True, "duplicate": True, "event": deepcopy(transaction_events[payload.idempotency_key])}
    event = {
        "receipt_reference": f"RCP-{uuid4().hex[:8].upper()}",
        "status": "accepted",
        "shop_reference": payload.shop_reference,
        "terminal_reference": payload.terminal_reference,
        "card_reference": normalise_reference(payload.card_reference),
        "items": [item.model_dump() for item in payload.items],
        "recorded_at": "2026-08-27T09:14:00+05:30",
    }
    transaction_events[payload.idempotency_key] = event
    return {"ok": True, "duplicate": False, "event": deepcopy(event)}


@app.post("/api/webhooks/stock")
def stock_webhook(payload: StockWebhook, authorization: Optional[str] = Header(default=None)) -> dict:
    """Accept a synthetic state/POS inventory update with replay protection."""
    require_shop_token(authorization)
    if not any(shop["reference"] == payload.shop_reference for shop in SHOPS):
        raise HTTPException(status_code=404, detail="Unknown synthetic shop reference.")
    if payload.idempotency_key in stock_events:
        return {"ok": True, "duplicate": True, "event": deepcopy(stock_events[payload.idempotency_key])}
    event = {"shop_reference": payload.shop_reference, "reported_at": payload.reported_at, "inventory": payload.inventory, "status": "accepted"}
    stock_events[payload.idempotency_key] = event
    return {"ok": True, "duplicate": False, "event": deepcopy(event)}


@app.post("/api/auth/request-otp")
def request_otp(payload: OTPRequest) -> dict:
    reference = normalise_reference(payload.card_reference)
    if reference not in {"DEMO-7824", "DEMO7824"}:
        return {"ok": False, "message": "This prototype only recognises the safe demo reference DEMO-7824."}
    challenge_id = f"demo-{uuid4().hex[:12]}"
    otp_challenges[challenge_id] = {"otp": DEMO_OTP, "reference": "DEMO-7824", "expires_at": time() + 600}
    return {
        "ok": True,
        "challenge_id": challenge_id,
        "masked_destination": "+91 •••••• 0198 (demo only)",
        "demo_otp": DEMO_OTP,
        "expires_in_seconds": 600,
        "message": "A synthetic OTP has been created. No SMS was sent.",
    }


@app.post("/api/auth/verify-otp")
def verify_otp(payload: OTPVerifyRequest) -> dict:
    challenge = otp_challenges.get(payload.challenge_id)
    if not challenge or challenge["expires_at"] < time():
        return {"ok": False, "message": "This OTP has expired. Request a new demo OTP."}
    if payload.otp != challenge["otp"]:
        return {"ok": False, "message": "That OTP is not correct. For the demo, use 246810."}
    session_token = f"demo-session-{uuid4().hex}"
    sessions[session_token] = {"card_reference": challenge["reference"], "created_at": time()}
    del otp_challenges[payload.challenge_id]
    return {"ok": True, "session_token": session_token, "profile": {"masked_household": DEMO_PROFILE["masked_household"], "state": DEMO_PROFILE["state"]}}


@app.get("/api/dashboard")
def dashboard(authorization: Optional[str] = Header(default=None), session_token: Optional[str] = Query(default=None)) -> dict:
    require_demo_session(authorization, session_token)
    return {"ok": True, "data": deepcopy(DEMO_PROFILE)}


@app.get("/api/shops")
def shops(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    onorc_only: bool = Query(default=False),
) -> dict:
    matches = SHOPS
    if state:
        matches = [shop for shop in matches if shop["state"].lower() == state.lower()]
    if district:
        matches = [shop for shop in matches if district.lower() in shop["district"].lower()]
    if onorc_only:
        matches = [shop for shop in matches if shop["onorc_enabled"]]
    return {"count": len(matches), "shops": deepcopy(matches), "data_status": "synthetic"}


@app.get("/api/shops/")
def shops_with_trailing_slash(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    onorc_only: bool = Query(default=False),
) -> dict:
    """Slash-tolerant alias for clients and hosted proxies that normalize URLs."""
    return shops(state=state, district=district, onorc_only=onorc_only)


@app.get("/api/complaints")
def complaints() -> dict:
    return {"count": len(COMPLAINTS), "complaints": deepcopy(COMPLAINTS), "data_status": "synthetic"}


@app.post("/api/complaints")
def create_complaint(payload: ComplaintCreate) -> dict:
    ticket = f"JR-{uuid4().hex[:6].upper()}"
    record = {
        "ticket": ticket,
        "category": payload.category,
        "shop": payload.store_reference or "Not specified",
        "created": "Today",
        "status": "Submitted",
        "status_key": "submitted",
        "update": "Your complaint has been queued for the district office. Next update within 3 working days.",
    }
    COMPLAINTS.insert(0, record)
    return {"ok": True, "complaint": deepcopy(record), "message": "Your synthetic complaint has been recorded."}


@app.post("/api/demo/reset")
def reset_demo_data(x_demo_reset_token: Optional[str] = Header(default=None)) -> dict[str, object]:
    """Reset synthetic complaints, updates, and event logs for hackathon testing."""
    expected = os.getenv("JANRATION_DEMO_RESET_TOKEN", "demo-reset-token")
    if x_demo_reset_token != expected:
        raise HTTPException(status_code=401, detail="A valid demo reset token is required.")
    COMPLAINTS.clear()
    COMPLAINTS.extend(deepcopy(INITIAL_COMPLAINTS))
    transaction_events.clear()
    stock_events.clear()
    return {"ok": True, "message": "Synthetic complaints, updates, and event logs reset.", "complaints": len(COMPLAINTS)}


@app.get("/api/portability")
def portability(home_state: str = Query(..., min_length=2), current_state: str = Query(..., min_length=2)) -> dict:
    same_state = home_state.strip().lower() == current_state.strip().lower()
    return {
        "eligible": True,
        "home_state": home_state.strip(),
        "current_state": current_state.strip(),
        "message": "Your home-state entitlement can be used at an ONORC-enabled shop here." if not same_state else "You can collect from a nearby shop in your home state.",
        "steps": [
            "Carry your ration card or state-approved reference.",
            "Ask for an ONORC-enabled Fair Price Shop.",
            "Check the quantity and price shown on the POS screen before confirming.",
        ],
        "shop_reference": "MH-PUN-2408" if not same_state else DEMO_PROFILE["home_shop_reference"],
    }


@app.get("/api/states")
def states() -> dict:
    return {"count": len(STATE_ADAPTERS), "states": deepcopy(STATE_ADAPTERS)}
