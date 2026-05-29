"""Calculation engine tests: unit conversion, region match, WTT, RFI."""
from decimal import Decimal
from datetime import datetime

import pytest

from app import models
from app.services.calculation_engine import CalculationEngine, _convert, _norm_unit

calc = CalculationEngine()


def test_norm_unit_folds_aliases():
    assert _norm_unit("Litres") == "L"
    assert _norm_unit("kilometers") == "KM"
    assert _norm_unit("Tonnes") == "TONNE"


def test_convert_round_trip_km_mi():
    one_km = Decimal("1.0")
    out = _convert(_convert(one_km, "KM", "MI"), "MI", "KM")
    assert abs(out - one_km) < Decimal("0.0001")


def test_convert_kwh_mwh():
    assert _convert(Decimal("1500"), "KWH", "MWH") == Decimal("1.500")


def test_convert_incompatible_raises():
    with pytest.raises(ValueError, match="Unit mismatch"):
        _convert(Decimal("1"), "KG", "KWH")


def test_calculate_with_unit_conversion(db, seeded_factors):
    # Diesel factor is per LITRES; supply gallons to force a conversion.
    result = calc.calculate(
        db, Decimal("10"), "GAL", "ENERGY", "diesel_generator", "UK"
    )
    # 10 gal -> 37.85 L * 2.546 kgCO2e/L ≈ 96.37
    assert Decimal("96") < result["kgco2e"] < Decimal("97")
    assert result["unit_converted"] is True
    assert result["region_match"] == "exact"
    assert result["scope"] == "SCOPE_1"


def test_calculate_unit_mismatch_raises(db, seeded_factors):
    with pytest.raises(ValueError, match="Unit mismatch"):
        calc.calculate(db, Decimal("10"), "KG", "ENERGY", "diesel_generator", "UK")


def test_calculate_records_region_fallback(db):
    # Seed a Global factor only.
    db.add(models.EmissionFactor(
        factor_id="factor-global-cat",
        standard="DEFRA",
        category="CATERING",
        subcategory="meals_mixed",
        activity_type="catering",
        factor_value=Decimal("1.5"),
        unit="KG",
        scope="SCOPE_3",
        region="Global",
        version="2024-v1",
        description="Generic catering",
        valid_from=datetime(2024, 1, 1),
        is_active=True,
    ))
    db.commit()
    result = calc.calculate(db, Decimal("100"), "KG", "CATERING", "meals_mixed", "UK")
    assert result["region_match"] == "global_fallback"


def test_calculate_aviation_rfi(db, seeded_factors):
    # Flight factor has RFI=1.7 in the fixture.
    result = calc.calculate(db, Decimal("1000"), "KM", "TRANSPORT", "short_haul_flight", "UK")
    # 1000 * 0.158 * 1.7 = 268.6
    assert abs(result["kgco2e"] - Decimal("268.6")) < Decimal("0.1")
    assert result["rfi_applied"] is True


def test_calculate_includes_total_with_wtt(db):
    # Factor with WTT to verify total = TTW + WTT.
    db.add(models.EmissionFactor(
        factor_id="factor-petrol-wtt",
        standard="DEFRA",
        category="ENERGY",
        subcategory="petrol",
        activity_type="fuel_combustion",
        factor_value=Decimal("2.0"),
        wtt_factor=Decimal("0.5"),
        unit="L",
        scope="SCOPE_1",
        region="UK",
        version="2024-v1",
        description="Petrol with WTT",
        valid_from=datetime(2024, 1, 1),
        is_active=True,
    ))
    db.commit()
    result = calc.calculate(db, Decimal("10"), "L", "ENERGY", "petrol", "UK")
    assert result["kgco2e"] == Decimal("20.0000")
    assert result["kgco2e_wtt"] == Decimal("5.0000")
    assert result["kgco2e_total"] == Decimal("25.0000")
