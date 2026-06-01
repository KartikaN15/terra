"""
Confidence Scoring Engine
Tiered confidence model with dynamic scoring.

Penalties are now sourced from the calculation result so the score reflects
the actual lookup quality (region match, unit conversion)   — not just static
factor metadata. The calc engine surfaces `region_match` and `unit_converted`
on every calculation; pass them through here.
"""
from decimal import Decimal
from datetime import date
from typing import Optional, Mapping, Any

from .. import models


BASE_SCORES = {
    "TIER_1_DIRECT": Decimal("0.95"),
    "TIER_2_BENCHMARK": Decimal("0.78"),
    "TIER_3_ML_IMPUTED": Decimal("0.55"),
}

# Centralised so policy is tunable in one place.
PENALTIES = {
    "old_factor": Decimal("0.05"),                # factor older than 2 years
    "expired_factor": Decimal("0.06"),            # factor's valid_to has passed
    "future_factor": Decimal("0.02"),             # factor's valid_from is in the future
    "cross_region_fallback": Decimal("0.15"),     # borrowed a factor from an unrelated region (no regional basis)
    "global_fallback": Decimal("0.08"),           # fell back from country/region to a global factor
    "continent_fallback": Decimal("0.05"),        # fell back to continent (EUROPE, AMERICAS …)
    "region_group_fallback": Decimal("0.03"),     # fell back to a group (EU, NA …)
    "region_fallback": Decimal("0.04"),           # legacy signal from older calc results
    "subcategory_parent_fallback": Decimal("0.04"),
    "missing_source_ref": Decimal("0.02"),
    "unit_converted": Decimal("0.01"),            # we converted units; small but auditable
    "classifier_scope": Decimal("0.03"),          # scope inferred from classifier, not factor
}


def determine_tier(source_type: str, source_reference: str) -> str:
    if source_type in ["IOT_STREAM", "MANUAL_ENTRY"] and source_reference:
        return "TIER_1_DIRECT"
    if source_type in ["INVOICE_OCR", "CSV_UPLOAD", "API_INTEGRATION"]:
        return "TIER_2_BENCHMARK"
    return "TIER_3_ML_IMPUTED"


def compute_score(
    tier: str,
    factor: Optional[models.EmissionFactor],
    source_ref: str,
    calc_result: Optional[Mapping[str, Any]] = None,
) -> Decimal:
    """Compute confidence score.

    `calc_result` is the dict returned by CalculationEngine.calculate; when
    provided we use its richer signals (region_match, unit_converted) instead
    of inferring them from the factor metadata alone.
    """
    score = BASE_SCORES.get(tier, Decimal("0.50"))

    # Penalty: old factor (>2 years)
    if factor and factor.valid_from:
        valid_from = factor.valid_from
        # valid_from may be either datetime or date depending on how it was loaded.
        valid_from_date = valid_from.date() if hasattr(valid_from, "date") else valid_from
        age_years = (date.today() - valid_from_date).days / 365
        if age_years > 2:
            score -= PENALTIES["old_factor"]

    # Penalty: region match. Prefer the calc-result signal when present —
    # it knows the request region, not just the factor metadata.
    region_match = (calc_result or {}).get("region_match")
    region_penalty_map = {
        "cross_region_fallback": PENALTIES["cross_region_fallback"],
        "global_fallback": PENALTIES["global_fallback"],
        "continent_fallback": PENALTIES["continent_fallback"],
        "region_group_fallback": PENALTIES["region_group_fallback"],
        "region_fallback": PENALTIES["region_fallback"],  # legacy
    }
    if region_match in region_penalty_map:
        score -= region_penalty_map[region_match]
    elif region_match is None:
        # Fallback to the legacy factor-only check for callers that don't
        # pass calc_result yet.
        if factor and factor.region == "Global" and not factor.country_code:
            score -= PENALTIES["global_fallback"]

    # Penalty: temporal mismatch.
    temporal_match = (calc_result or {}).get("temporal_match")
    if temporal_match == "expired":
        score -= PENALTIES["expired_factor"]
    elif temporal_match == "future":
        score -= PENALTIES["future_factor"]

    # Penalty: subcategory was a parent fallback ("diesel_generator_50kva" → "diesel_generator").
    if (calc_result or {}).get("subcategory_match") == "parent_fallback":
        score -= PENALTIES["subcategory_parent_fallback"]

    # Penalty: missing source reference
    if not source_ref:
        score -= PENALTIES["missing_source_ref"]

    # Penalty: a unit conversion was needed. Small, but flags any data-quality
    # problem upstream where activity values aren't being captured in the
    # factor's native unit.
    if (calc_result or {}).get("unit_converted"):
        score -= PENALTIES["unit_converted"]

    return max(Decimal("0.0"), min(Decimal("1.0"), score))
