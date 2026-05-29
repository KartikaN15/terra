"""Tests for ML API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_ml_health(client):
    response = client.get("/api/v1/ml/health")
    assert response.status_code == 200
    data = response.json()
    assert "greenlight_loaded" in data


def test_ml_forecast_without_model(client):
    response = client.post("/api/v1/ml/forecast/greenlight", json={
        "project_id": "test-001",
        "metadata": {
            "project_type": "FEATURE",
            "scale_band": "_1M_TO_5M",
            "duration": 30,
            "headcount": 50,
            "complexity": "LOW",
            "output_units": 1,
            "output_size": 90,
            "region": "UK",
        },
    })
    # Without trained model, may return 503 or stub result
    assert response.status_code in (200, 503)
