"""
Calculation Engine
ActivityEvent + EmissionFactor -> kgCO2e

Guardrails:
- Unit compatibility is enforced. If the event unit cannot be converted to the
  factor's unit, raise   — silent multiplication of mismatched units is exactly
  the kind of bug that destroys auditability.
- Factor selection is delegated to `factor_resolver` so region hierarchy,
  temporal validity, and subcategory fallback are handled centrally and
  graded; the grade is surfaced to the caller for confidence scoring.
- The calc result includes the resolved factor row itself so the API layer
  doesn't need a second `get_factor()` round-trip.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from .. import crud, models
from .factor_resolver import resolve as resolve_factor


# Conversion factors expressed as: 1 unit_from = N * unit_to.
# Keys are normalised UPPER; aliases are folded in _norm_unit.
_UNIT_CONVERSIONS: dict[Tuple[str, str], Decimal] = {
    # distance
    ("KM", "MI"): Decimal("0.621371"),
    ("MI", "KM"): Decimal("1.609344"),
    ("KM", "M"): Decimal("1000"),
    ("M", "KM"): Decimal("0.001"),
    # energy
    ("KWH", "MWH"): Decimal("0.001"),
    ("MWH", "KWH"): Decimal("1000"),
    ("KWH", "GJ"): Decimal("0.0036"),
    ("GJ", "KWH"): Decimal("277.777778"),
    # mass
    ("KG", "TONNE"): Decimal("0.001"),
    ("TONNE", "KG"): Decimal("1000"),
    ("G", "KG"): Decimal("0.001"),
    ("KG", "G"): Decimal("1000"),
    # volume
    ("L", "GAL"): Decimal("0.264172"),  # US gallon
    ("GAL", "L"): Decimal("3.785412"),
    ("L", "M3"): Decimal("0.001"),
    ("M3", "L"): Decimal("1000"),
}

_UNIT_ALIASES = {
    "LITRE": "L", "LITRES": "L", "LITER": "L", "LITERS": "L",
    "GALLON": "GAL", "GALLONS": "GAL",
    "KILOMETRE": "KM", "KILOMETER": "KM", "KILOMETRES": "KM", "KILOMETERS": "KM",
    "MILE": "MI", "MILES": "MI",
    "METRE": "M", "METER": "M", "METRES": "M", "METERS": "M",
    "TONNES": "TONNE", "TON": "TONNE", "TONS": "TONNE", "MT": "TONNE",
    "KILOGRAM": "KG", "KILOGRAMS": "KG", "KGS": "KG",
    "GRAM": "G", "GRAMS": "G",
}


def _norm_unit(unit: str) -> str:
    u = (unit or "").strip().upper()
    return _UNIT_ALIASES.get(u, u)


def _convert(value: Decimal, from_unit: str, to_unit: str) -> Decimal:
    """Convert value from one unit to another. Raises if incompatible."""
    a, b = _norm_unit(from_unit), _norm_unit(to_unit)
    if a == b:
        return value
    factor = _UNIT_CONVERSIONS.get((a, b))
    if factor is None:
        raise ValueError(
            f"Unit mismatch: cannot convert '{from_unit}' to '{to_unit}'. "
            "Add an entry to _UNIT_CONVERSIONS or supply the value in the factor's native unit."
        )
    return value * factor


class CalculationEngine:
    """Core engine: converts activity data + emission factor -> kgCO2e."""

    def calculate(
        self,
        db: Session,
        value: Decimal,
        unit: str,
        category: str,
        subcategory: str,
        region: str,
        standard: Optional[str] = None,
        as_of: Optional[date] = None,
    ) -> dict:
        resolved = resolve_factor(db, category, subcategory, region, standard, as_of=as_of)
        if not resolved:
            raise ValueError(f"No emission factor found for {subcategory} in {region}")

        factor = resolved.factor
        quality = resolved.quality

        # Normalise the activity value to the factor's unit BEFORE multiplying.
        # Mismatched units would otherwise silently produce wrong numbers.
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        converted_value = _convert(value, unit, factor.unit)

        kgco2e_ttw = converted_value * factor.factor_value

        # Radiative Forcing Index for aviation (DEFRA recommends 1.9 to account
        # for non-CO2 warming effects at altitude; seeded per flight factor row).
        # We track the uplift component separately so reports can show the
        # tank-to-wheel base + the RFI add-on.
        rfi_uplift = Decimal("0")
        rfi_applied = False
        if factor.category == "TRANSPORT" and "flight" in (factor.subcategory or ""):
            rfi = factor.radiative_forcing_multiplier or Decimal("1.0")
            if rfi != Decimal("1.0"):
                rfi_uplift = kgco2e_ttw * (rfi - Decimal("1.0"))
                rfi_applied = True

        # Well-to-tank
        kgco2e_wtt = converted_value * factor.wtt_factor if factor.wtt_factor else Decimal("0")

        # `kgco2e` is the headline operational footprint (combustion +
        # RFI uplift for flights). WTT is reported separately so reports can
        # show TTW + WTT splits without double-counting.
        kgco2e_headline = kgco2e_ttw + rfi_uplift
        kgco2e_total = kgco2e_headline + kgco2e_wtt

        return {
            # Headline footprint persisted on the event row. For flights this
            # already includes the RFI uplift, matching how DEFRA reports.
            "kgco2e": round(kgco2e_headline, 4),
            # Structured breakdown — preferred for new code.
            "breakdown": {
                "ttw": round(kgco2e_ttw, 4),
                "rfi_uplift": round(rfi_uplift, 4),
                "wtt": round(kgco2e_wtt, 4) if kgco2e_wtt else Decimal("0"),
                "total": round(kgco2e_total, 4),
            },
            "kgco2e_wtt": round(kgco2e_wtt, 4) if kgco2e_wtt else None,
            "kgco2e_total": round(kgco2e_total, 4),
            "factor": factor,                     # NEW: pass-through; saves a DB hit
            "factor_id": factor.factor_id,
            "factor_version": factor.version,
            "factor_unit": factor.unit,
            "scope": factor.scope,
            "gwp_version": getattr(factor, "gwp_version", None) or "AR5",
            "unit_converted": _norm_unit(unit) != _norm_unit(factor.unit),
            "rfi_applied": rfi_applied,
            # Match-quality block. Persisted on the event for audit + drives
            # confidence scoring.
            "region_match": quality.region,
            "subcategory_match": quality.subcategory,
            "temporal_match": quality.temporal,
            "calculation_method": f"activity_based_{factor.standard}",
        }
