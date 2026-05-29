"""Audit integrity tests: ActivityEvent must always carry factor_id + version."""
from datetime import datetime
from decimal import Decimal

import pytest

from app import models
from app.models import AuditIntegrityError


def _base_event(production_id: str, **overrides):
    defaults = dict(
        event_id="event-test-001",
        production_id=production_id,
        phase="PRODUCTION",
        scope="SCOPE_1",
        category="ENERGY",
        subcategory="diesel_generator",
        value=Decimal("10.0"),
        unit="LITRES",
        kgco2e=Decimal("25.46"),
        confidence_tier="TIER_1_DIRECT",
        confidence_score=Decimal("0.95"),
        source_type="MANUAL_ENTRY",
        recorded_by="user-001",
        recorded_at=datetime(2024, 3, 15, 10, 0, 0),
        calculation_method="activity_based_DEFRA",
        emission_factor_id="factor-diesel-uk",
        emission_factor_version="2024-v1",
    )
    defaults.update(overrides)
    return models.ActivityEvent(**defaults)


def test_insert_rejected_without_factor_id(db, seeded_factors, sample_production):
    evt = _base_event(sample_production.production_id, emission_factor_id=None)
    db.add(evt)
    with pytest.raises(AuditIntegrityError, match="emission_factor_id"):
        db.flush()
    db.rollback()


def test_insert_rejected_with_blank_factor_id(db, seeded_factors, sample_production):
    evt = _base_event(sample_production.production_id, emission_factor_id="   ")
    db.add(evt)
    with pytest.raises(AuditIntegrityError, match="emission_factor_id"):
        db.flush()
    db.rollback()


def test_insert_rejected_without_factor_version(db, seeded_factors, sample_production):
    evt = _base_event(sample_production.production_id, emission_factor_version=None)
    db.add(evt)
    with pytest.raises(AuditIntegrityError, match="emission_factor_version"):
        db.flush()
    db.rollback()


def test_update_rejected_when_clearing_factor_fields(db, seeded_factors, sample_production):
    evt = _base_event(sample_production.production_id)
    db.add(evt)
    db.commit()

    evt.emission_factor_version = ""
    with pytest.raises(AuditIntegrityError, match="emission_factor_version"):
        db.flush()
    db.rollback()


def test_insert_succeeds_with_full_audit_fields(db, seeded_factors, sample_production):
    evt = _base_event(sample_production.production_id)
    db.add(evt)
    db.flush()
    db.commit()
    assert evt.emission_factor_id == "factor-diesel-uk"
    assert evt.emission_factor_version == "2024-v1"
