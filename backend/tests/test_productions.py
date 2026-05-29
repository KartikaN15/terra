"""Production CRUD API tests."""
from decimal import Decimal


def test_create_production(client):
    payload = {
        "production_id": "prod-001",
        "title": "Epic Fantasy",
        "type": "FEATURE",
        "genre": "FANTASY",
        "budget_band": "_10M_TO_50M",
        "runtime_min": 150,
        "episodes": 1,
        "shoot_days": 45,
        "locations": ["NZ", "UK"],
        "cast_count": 20,
        "crew_count": 120,
        "vfx_intensity": "HIGH",
        "status": "PRE_PRODUCTION",
    }
    response = client.post("/api/v1/productions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["production_id"] == "prod-001"
    assert data["title"] == "Epic Fantasy"
    assert data["genre"] == "FANTASY"


def test_list_productions(client, sample_production):
    response = client.get("/api/v1/productions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["production_id"] == sample_production.production_id for p in data)


def test_get_production(client, sample_production):
    response = client.get(f"/api/v1/productions/{sample_production.production_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Production"


def test_get_production_not_found(client):
    response = client.get("/api/v1/productions/non-existent-id")
    assert response.status_code == 404


def test_update_production(client, sample_production):
    response = client.patch(
        f"/api/v1/productions/{sample_production.production_id}",
        json={"title": "Updated Title", "status": "POST_PRODUCTION"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "POST_PRODUCTION"


def test_delete_production(client, sample_production):
    response = client.delete(f"/api/v1/productions/{sample_production.production_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    response = client.get(f"/api/v1/productions/{sample_production.production_id}")
    assert response.status_code == 404


def test_production_summary_no_events(client, sample_production):
    response = client.get(f"/api/v1/productions/{sample_production.production_id}/summary")
    assert response.status_code == 404
