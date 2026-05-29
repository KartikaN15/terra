"""Pytest fixtures for backend API tests."""
import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Ensure ml_engine is importable and set env vars BEFORE any app imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["MODEL_DIR"] = str(PROJECT_ROOT / "ml_models")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

# Import app modules AFTER env vars are set
from app.database import engine, Base, SessionLocal, get_db
from app.main import app
from app import crud, schemas, models


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test function."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Return a TestClient with DB session override."""
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def seeded_factors(db):
    """Seed a small set of emission factors for testing."""
    factors = [
        models.EmissionFactor(
            factor_id="factor-diesel-uk",
            standard="DEFRA",
            category="ENERGY",
            subcategory="diesel_generator",
            activity_type="fuel_combustion",
            factor_value=Decimal("2.546"),
            unit="LITRES",
            scope="SCOPE_1",
            region="UK",
            country_code="GB",
            version="2024-v1",
            description="Diesel generator",
            valid_from=datetime(2024, 1, 1),
            is_active=True,
        ),
        models.EmissionFactor(
            factor_id="factor-grid-uk",
            standard="DEFRA",
            category="ENERGY",
            subcategory="grid_electricity",
            activity_type="electricity",
            factor_value=Decimal("0.207"),
            unit="KWH",
            scope="SCOPE_2",
            region="UK",
            country_code="GB",
            grid_intensity_g_co2_kwh=Decimal("207"),
            version="2024-v1",
            description="UK grid electricity",
            valid_from=datetime(2024, 1, 1),
            is_active=True,
        ),
        models.EmissionFactor(
            factor_id="factor-flight-uk",
            standard="DEFRA",
            category="TRANSPORT",
            subcategory="short_haul_flight",
            activity_type="air_travel",
            factor_value=Decimal("0.158"),
            unit="KM",
            scope="SCOPE_3",
            region="UK",
            country_code="GB",
            version="2024-v1",
            description="Short haul flight",
            valid_from=datetime(2024, 1, 1),
            is_active=True,
            radiative_forcing_multiplier=Decimal("1.7"),
        ),
    ]
    db.add_all(factors)
    db.commit()
    return factors


@pytest.fixture(scope="function")
def sample_production(db):
    """Create a sample production."""
    prod = crud.create_production(
        db,
        schemas.ProductionCreate(
            production_id="prod-test-001",
            title="Test Production",
            type="FEATURE",
            genre="DRAMA",
            budget_band="_1M_TO_5M",
            runtime_min=120,
            episodes=1,
            shoot_days=30,
            locations=["UK", "ES"],
            cast_count=10,
            crew_count=50,
            vfx_intensity="LOW",
            status="PRODUCTION",
        ),
        created_by="user-001",
    )
    return prod
