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


def test_resolver_cross_region_fallback(db, seeded_factors):
    """A region with no factor of its own (IND) borrows the factor from any
    available region as a last resort, graded `cross_region_fallback`, so the
    calculation never silently drops the activity."""
    from app.services.factor_resolver import resolve

    resolved = resolve(db, "ENERGY", "diesel_generator", "IND")
    assert resolved is not None
    assert resolved.factor.region == "UK"  # borrowed from the only seeded region
    assert resolved.quality.region == "cross_region_fallback"


def test_resolver_returns_none_when_subcategory_absent(db, seeded_factors):
    """Cross-region fallback only kicks in when the subcategory exists somewhere.
    A subcategory absent from every region still resolves to None."""
    from app.services.factor_resolver import resolve

    assert resolve(db, "ENERGY", "fusion_reactor", "IND") is None


def test_create_event_cross_region_fallback(client, seeded_factors, sample_production):
    """Logging an activity for a region with no local factor still succeeds and
    persists an auditable kgco2e (the exact diesel_generator/IND case)."""
    payload = {
        "production_id": sample_production.production_id,
        "recorded_by": "tester",
        "phase": "PRODUCTION",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "23456",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "source_reference": "123",
        "grid_region": "IND",
        "recorded_at": "2026-06-01T11:01:00",
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    # 23456 LITRES * 2.546 = 59718.976
    assert float(data["kgco2e"]) == 59718.976
    assert data["emission_factor_id"] is not None  # auditability preserved
