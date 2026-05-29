"""Emission Factor API tests."""
from datetime import datetime
from decimal import Decimal


def test_create_factor(client):
    payload = {
        "standard": "EPA",
        "category": "WASTE",
        "subcategory": "landfill_general",
        "activity_type": "disposal",
        "factor_value": "0.5",
        "unit": "KG",
        "scope": "SCOPE_3",
        "region": "US",
        "country_code": "US",
        "version": "2024-v1",
        "description": "General landfill",
        "valid_from": datetime(2024, 1, 1).isoformat(),
        "radiative_forcing_multiplier": "1.0",
    }
    response = client.post("/api/v1/factors", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "WASTE"
    assert data["factor_id"] is not None


def test_list_factors(client, seeded_factors):
    response = client.get("/api/v1/factors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_list_factors_filtered(client, seeded_factors):
    response = client.get("/api/v1/factors?category=ENERGY&region=UK")
    assert response.status_code == 200
    data = response.json()
    assert all(f["category"] == "ENERGY" for f in data)


def test_lookup_factor_found(client, seeded_factors):
    response = client.get("/api/v1/factors/lookup?category=ENERGY&subcategory=diesel_generator&region=UK")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["factor"]["subcategory"] == "diesel_generator"


def test_lookup_factor_not_found(client):
    response = client.get("/api/v1/factors/lookup?category=MAGIC&subcategory=unicorn_dust&region=UK")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is False
