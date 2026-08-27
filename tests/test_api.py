from fastapi.testclient import TestClient
from pathlib import Path

from app import app


client = TestClient(app)
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def test_health_endpoint_is_demo_mode():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "demo"


def test_plain_language_bar_is_present_and_persistent():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert 'id="plain-language-toggle"' in html
    assert "janration-plain-language" in javascript
    assert "aria-pressed" in javascript


def test_demo_entitlement_requires_safe_reference():
    response = client.post("/api/entitlement", json={"card_reference": "DEMO-7824"})
    assert response.status_code == 200
    assert response.json()["found"] is True
    assert response.json()["data"]["items"][0]["quantity"] == "20 kg"


def test_unknown_entitlement_is_explained():
    response = client.post("/api/entitlement", json={"card_reference": "REAL-1234"})
    assert response.status_code == 200
    assert response.json()["found"] is False


def test_shop_filter():
    response = client.get("/api/shops", params={"state": "Maharashtra"})
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["shops"][0]["district"] == "Pune"
    assert response.json()["shops"][0]["queue_minutes"] == 8
    assert response.json()["shops"][0]["wheelchair_accessible"] is True


def test_state_adapter_catalog_is_explicit():
    response = client.get("/api/states")
    assert response.status_code == 200
    assert response.json()["count"] == 3
    assert response.json()["states"][0]["adapter"] == "tnpds"


def test_onorc_portability_guidance_is_synthetic():
    response = client.get("/api/portability", params={"home_state": "Tamil Nadu", "current_state": "Maharashtra"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["eligible"] is True
    assert len(payload["steps"]) == 3


def test_grievance_returns_trackable_ticket():
    response = client.post("/api/grievances", json={"category": "Shop was closed", "description": "The shop was closed during the displayed hours."})
    assert response.status_code == 200
    assert response.json()["ticket"].startswith("JR-")
