"""Activity Event API tests."""
from datetime import datetime
from decimal import Decimal


def test_create_event(client, seeded_factors, sample_production):
    payload = {
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_1",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "100.0",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "source_reference": "fuel_log_001",
        "grid_region": "UK",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["production_id"] == sample_production.production_id
    assert data["category"] == "ENERGY"
    assert data["subcategory"] == "diesel_generator"
    assert float(data["kgco2e"]) > 0
    assert data["confidence_tier"] == "TIER_1_DIRECT"
    assert data["calculation_method"] == "activity_based_DEFRA"


def test_create_event_unknown_subcategory(client, sample_production):
    payload = {
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_1",
        "category": "ENERGY",
        "subcategory": "fusion_reactor",
        "value": "100.0",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 422


def test_list_events_by_production(client, seeded_factors, sample_production):
    # Create two events
    for val in [50, 100]:
        client.post("/api/v1/events", json={
            "production_id": sample_production.production_id,
            "phase": "PRODUCTION",
            "scope": "SCOPE_1",
            "category": "ENERGY",
            "subcategory": "diesel_generator",
            "value": str(val),
            "unit": "LITRES",
            "source_type": "MANUAL_ENTRY",
            "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
            "recorded_by": "user-001",
        })

    response = client.get(f"/api/v1/events/production/{sample_production.production_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_event(client, seeded_factors, sample_production):
    create_resp = client.post("/api/v1/events", json={
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_1",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "75.0",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    })
    event_id = create_resp.json()["event_id"]

    response = client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == event_id


def test_delete_event(client, seeded_factors, sample_production):
    create_resp = client.post("/api/v1/events", json={
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_1",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "75.0",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    })
    event_id = create_resp.json()["event_id"]

    response = client.delete(f"/api/v1/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    response = client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 404


def test_production_summary_with_events(client, seeded_factors, sample_production):
    client.post("/api/v1/events", json={
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_1",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "100.0",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    })

    response = client.get(f"/api/v1/productions/{sample_production.production_id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_tco2e"]) > 0
    assert data["event_count"] == 1
    assert "SCOPE_1" in data["scope_breakdown"]


def test_bulk_upload_events(client, seeded_factors, sample_production):
    csv_content = (
        "production_id,phase,category,subcategory,value,unit,source_type,recorded_at,recorded_by\n"
        f"{sample_production.production_id},PRODUCTION,ENERGY,diesel_generator,100,LITRES,MANUAL_ENTRY,2024-03-15T10:00:00,user-001\n"
        f"{sample_production.production_id},PRODUCTION,ENERGY,grid_electricity,500,KWH,MANUAL_ENTRY,2024-03-16T10:00:00,user-001\n"
    )
    response = client.post(
        "/api/v1/events/bulk-upload",
        files={"file": ("events.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "events.csv"
    assert data["total_rows"] == 2
    assert data["created"] == 2
    assert len(data["errors"]) == 0


def test_bulk_upload_missing_required_column(client):
    csv_content = (
        "production_id,phase,category,subcategory,value,unit,source_type,recorded_by\n"
        "prod-001,PRODUCTION,ENERGY,diesel_generator,100,LITRES,MANUAL_ENTRY,user-001\n"
    )
    response = client.post(
        "/api/v1/events/bulk-upload",
        files={"file": ("events.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 422
    data = response.json()
    assert "Missing required columns" in str(data["detail"])


def test_bulk_upload_invalid_production(client, seeded_factors):
    csv_content = (
        "production_id,phase,category,subcategory,value,unit,source_type,recorded_at,recorded_by\n"
        "non-existent-prod,PRODUCTION,ENERGY,diesel_generator,100,LITRES,MANUAL_ENTRY,2024-03-15T10:00:00,user-001\n"
    )
    response = client.post(
        "/api/v1/events/bulk-upload",
        files={"file": ("events.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 1
    assert data["created"] == 0
    assert len(data["errors"]) == 1
    assert "not found" in data["errors"][0]["message"]


def test_event_persists_audit_columns(client, seeded_factors, sample_production):
    """gwp_version, region_match, unit_converted must land on the saved row
    so audit queries don't have to re-derive them from the factor."""
    payload = {
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_1",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "10.0",
        "unit": "GAL",  # forces a unit conversion vs the LITRES factor
        "source_type": "MANUAL_ENTRY",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["unit_converted"] is True
    assert body["region_match"] == "exact"
    assert body["gwp_version"] in ("AR5", "AR6")


def test_factor_scope_overrides_user_supplied_scope(client, seeded_factors, sample_production):
    # User claims SCOPE_3, but the diesel_generator factor is SCOPE_1.
    # The factor must win so audit and reporting stay consistent.
    payload = {
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_3",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "100.0",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 200
    assert response.json()["scope"] == "SCOPE_1"


def test_patch_event(client, seeded_factors, sample_production):
    create_resp = client.post("/api/v1/events", json={
        "production_id": sample_production.production_id,
        "phase": "PRODUCTION",
        "scope": "SCOPE_1",
        "category": "ENERGY",
        "subcategory": "diesel_generator",
        "value": "75.0",
        "unit": "LITRES",
        "source_type": "MANUAL_ENTRY",
        "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
        "recorded_by": "user-001",
    })
    event_id = create_resp.json()["event_id"]

    response = client.patch(f"/api/v1/events/{event_id}", json={
        "value": "150.0",
        "notes": "updated value",
    })
    assert response.status_code == 200
    data = response.json()
    assert float(data["value"]) == 150.0
    assert data["notes"] == "updated value"
    # kgco2e should NOT change on patch (use recalculate for that)
    assert float(data["kgco2e"]) == float(create_resp.json()["kgco2e"])


def test_list_events_pagination(client, seeded_factors, sample_production):
    for val in [10, 20, 30]:
        client.post("/api/v1/events", json={
            "production_id": sample_production.production_id,
            "phase": "PRODUCTION",
            "scope": "SCOPE_1",
            "category": "ENERGY",
            "subcategory": "diesel_generator",
            "value": str(val),
            "unit": "LITRES",
            "source_type": "MANUAL_ENTRY",
            "recorded_at": datetime(2024, 3, 15, 10, 0, 0).isoformat(),
            "recorded_by": "user-001",
        })
    response = client.get(f"/api/v1/events/production/{sample_production.production_id}?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_bulk_upload_invalid_file_type(client):
    response = client.post(
        "/api/v1/events/bulk-upload",
        files={"file": ("events.txt", "not a csv", "text/plain")},
    )
    assert response.status_code == 400
