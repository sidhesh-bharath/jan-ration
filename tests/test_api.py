from pathlib import Path

from fastapi.testclient import TestClient

from app import DEMO_OTP, app


client = TestClient(app)
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def get_demo_session() -> str:
    challenge = client.post("/api/auth/request-otp", json={"card_reference": "DEMO-7824"}).json()
    response = client.post("/api/auth/verify-otp", json={"challenge_id": challenge["challenge_id"], "otp": DEMO_OTP})
    return response.json()["session_token"]


def test_home_and_developer_routes_are_branded():
    assert client.get("/").status_code == 200
    assert client.get("/developers").status_code == 200
    developer_html = (STATIC_DIR / "developers.html").read_text(encoding="utf-8")
    assert "JanRation" in developer_html
    assert "jan-ration.vercel.app" in developer_html
    assert "onrender.com" not in developer_html
    assert "YOUR-RENDER-SERVICE" not in developer_html
    portal_html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    assert 'id="plain-language-toggle"' in portal_html
    assert 'data-i18n="plainLanguageTitle"' in portal_html
    assert (STATIC_DIR / "favicon.svg").exists()


def test_health_is_synthetic_only():
    payload = client.get("/api/health").json()
    assert payload["service"] == "JanRation API"
    assert payload["product"] == "JanRation"
    assert payload["data_policy"] == "synthetic-only"


def test_dummy_otp_flow_issues_a_session():
    challenge = client.post("/api/auth/request-otp", json={"card_reference": "DEMO-7824"}).json()
    assert challenge["ok"] is True
    assert challenge["demo_otp"] == "246810"
    verified = client.post("/api/auth/verify-otp", json={"challenge_id": challenge["challenge_id"], "otp": "246810"}).json()
    assert verified["ok"] is True
    assert verified["session_token"].startswith("demo-session-")


def test_dashboard_requires_verified_session_and_returns_allocation_bars_data():
    assert client.get("/api/dashboard").status_code == 401
    response = client.get("/api/dashboard", params={"session_token": get_demo_session()})
    assert response.status_code == 200
    assert response.json()["data"]["allocations"][0]["withdrawn"] == 12
    assert len(response.json()["data"]["transactions"]) == 5


def test_shop_filter_and_map_metadata():
    response = client.get("/api/shops", params={"state": "Maharashtra", "onorc_only": True})
    assert response.status_code == 200
    shop = response.json()["shops"][0]
    assert shop["reference"] == "MH-PUN-2408"
    assert shop["map_x"] == 43
    assert shop["onorc_enabled"] is True


def test_shop_endpoint_accepts_trailing_slash_and_demo_reset_is_protected():
    assert client.get("/api/shops/", params={"state": "Tamil Nadu"}).status_code == 200
    assert client.post("/api/demo/reset").status_code == 401
    assert client.post("/api/demo/reset", headers={"X-Demo-Reset-Token": "demo-reset-token"}).status_code == 200


def test_complaints_are_prepopulated_and_new_ticket_is_trackable():
    existing = client.get("/api/complaints").json()
    assert existing["count"] >= 3
    created = client.post("/api/complaints", json={"category": "Shop was closed", "description": "The demo shop was closed during the displayed hours.", "store_reference": "TN-CHN-1042"}).json()
    assert created["ok"] is True
    assert created["complaint"]["ticket"].startswith("JR-")


def test_portability_and_adapter_catalog_are_available():
    portability = client.get("/api/portability", params={"home_state": "Tamil Nadu", "current_state": "Maharashtra"}).json()
    assert portability["eligible"] is True
    assert len(portability["steps"]) == 3
    states = client.get("/api/states").json()
    assert states["count"] >= 5
    assert states["states"][0]["adapter"] == "tnpds"


def test_shop_transaction_is_idempotent():
    body = {"shop_reference": "TN-CHN-1042", "terminal_reference": "POS-TN-1042-A", "card_reference": "DEMO-7824", "idempotency_key": "demo-lift-0001", "items": [{"name": "Rice", "quantity": 2, "unit": "kg"}]}
    first = client.post("/api/transactions", headers={"Authorization": "Bearer demo-shop-token"}, json=body)
    second = client.post("/api/transactions", headers={"Authorization": "Bearer demo-shop-token"}, json=body)
    assert first.status_code == 200
    assert second.json()["duplicate"] is True
    assert second.json()["event"]["receipt_reference"] == first.json()["event"]["receipt_reference"]


def test_stock_webhook_rejects_missing_shop_token_and_accepts_a_safe_retry():
    body = {"shop_reference": "TN-CHN-1042", "idempotency_key": "demo-stock-0001", "reported_at": "2026-08-27T09:15:00+05:30", "inventory": [{"name": "Rice", "available": "High"}]}
    assert client.post("/api/webhooks/stock", json=body).status_code == 401
    response = client.post("/api/webhooks/stock", headers={"Authorization": "Bearer demo-shop-token"}, json=body)
    assert response.status_code == 200
    assert response.json()["event"]["status"] == "accepted"
