from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_endpoint_is_demo_mode():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "demo"


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


def test_grievance_returns_trackable_ticket():
    response = client.post("/api/grievances", json={"category": "Shop was closed", "description": "The shop was closed during the displayed hours."})
    assert response.status_code == 200
    assert response.json()["ticket"].startswith("JR-")
