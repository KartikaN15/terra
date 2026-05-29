"""Confidence scorer: penalties for region fallback, unit conversion, etc."""
from datetime import datetime
from decimal import Decimal

from app import models
from app.services.confidence_scorer import compute_score, PENALTIES, BASE_SCORES


def _factor(**over):
    base = dict(
        factor_id="f-1", standard="DEFRA", category="ENERGY",
        subcategory="diesel_generator", activity_type="fuel_combustion",
        factor_value=Decimal("2.5"), unit="L", scope="SCOPE_1",
        region="UK", country_code="GB", version="2025-v1",
        description="d", valid_from=datetime(2025, 6, 1), is_active="true",
    )
    base.update(over)
    return models.EmissionFactor(**base)


def test_exact_region_no_penalty():
    f = _factor()
    score = compute_score("TIER_1_DIRECT", f, "ref-1", calc_result={"region_match": "exact"})
    assert score == BASE_SCORES["TIER_1_DIRECT"]


def test_global_fallback_penalised():
    f = _factor(region="Global", country_code=None)
    score = compute_score("TIER_1_DIRECT", f, "ref-1", calc_result={"region_match": "global_fallback"})
    assert score == BASE_SCORES["TIER_1_DIRECT"] - PENALTIES["global_fallback"]


def test_region_fallback_lighter_than_global():
    f = _factor()
    region = compute_score("TIER_1_DIRECT", f, "ref-1", calc_result={"region_match": "region_fallback"})
    glob = compute_score("TIER_1_DIRECT", f, "ref-1", calc_result={"region_match": "global_fallback"})
    assert region > glob


def test_unit_conversion_penalty_applied():
    f = _factor()
    base = compute_score("TIER_1_DIRECT", f, "ref", calc_result={"region_match": "exact"})
    converted = compute_score("TIER_1_DIRECT", f, "ref", calc_result={"region_match": "exact", "unit_converted": True})
    assert base - converted == PENALTIES["unit_converted"]


def test_missing_source_ref_penalised():
    f = _factor()
    with_ref = compute_score("TIER_1_DIRECT", f, "ref-1", calc_result={"region_match": "exact"})
    no_ref = compute_score("TIER_1_DIRECT", f, "", calc_result={"region_match": "exact"})
    assert with_ref - no_ref == PENALTIES["missing_source_ref"]


def test_legacy_call_without_calc_result_still_works():
    """compute_score must not break callers that don't pass calc_result yet."""
    f = _factor(region="Global", country_code=None)
    score = compute_score("TIER_1_DIRECT", f, "ref")
    # Falls back to factor-only logic and applies the global penalty.
    assert score == BASE_SCORES["TIER_1_DIRECT"] - PENALTIES["global_fallback"]


def test_score_clamped_to_unit_interval():
    f = _factor(valid_from=datetime(2010, 1, 1), region="Global", country_code=None)
    score = compute_score(
        "TIER_3_ML_IMPUTED", f, "",
        calc_result={"region_match": "global_fallback", "unit_converted": True},
    )
    assert Decimal("0") <= score <= Decimal("1")
