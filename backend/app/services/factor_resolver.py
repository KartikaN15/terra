"""
Emission Factor Resolver
========================

Centralised, dynamic lookup for the "best" EmissionFactor row given a request
(category, subcategory, region, optional standard, optional as-of date).

Goals over the previous flat lookup:
- Country alias normalisation (UK ↔ GB, USA ↔ US, …) so factor rows seeded with
  ISO codes still resolve when callers pass colloquial names.
- Region hierarchy fallback: country → region group (EU / NA / …) → continent
  → Global. Each step is graded so confidence scoring can penalise fallbacks
  proportionally.
- Temporal validity: prefer factors current as-of `as_of` (default: today). An
  expired factor is still returned as a last resort, but flagged.
- Version preference: when multiple factors tie on (category, subcategory,
  region), the highest version wins.
- Subcategory fallback: if the exact subcategory misses, try parent
  ("diesel_generator_50kva" → "diesel_generator") so factor libraries don't
  need to enumerate every variant.

The output is a `ResolvedFactor` carrying the row plus a match-quality block.
The match-quality block is what the confidence scorer reads to grade the
result; downstream callers should not re-derive it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models


# ---- Region / country knowledge --------------------------------------------

# Map common aliases to the canonical token used in seed data. Keys are
# normalised UPPER. Canonical values mirror what `seed_emission_factors.py`
# writes into `region` / `country_code`.
COUNTRY_ALIASES: dict[str, str] = {
    "UK": "GB", "GBR": "GB", "GREAT BRITAIN": "GB",
    "UNITED KINGDOM": "GB", "ENGLAND": "GB", "BRITAIN": "GB",
    "USA": "US", "U.S.": "US", "U.S.A.": "US", "UNITED STATES": "US",
    "AMERICA": "US",
    "DEUTSCHLAND": "DE", "GERMANY": "DE",
    "FRANCE": "FR",
    "ESPANA": "ES", "ESPAÑA": "ES", "SPAIN": "ES",
    "ITALIA": "IT", "ITALY": "IT",
    "NEDERLAND": "NL", "NETHERLANDS": "NL", "HOLLAND": "NL",
    "INDIA": "IN",
    "CHINA": "CN",
    "JAPAN": "JP",
    "AUSTRALIA": "AU",
    "CANADA": "CA",
}

# Hierarchical fallback chain per canonical country.  When an exact-country
# factor is missing we walk this chain looking for the first match. Each
# successive step is "further away" and graded accordingly.
REGION_HIERARCHY: dict[str, List[str]] = {
    "GB": ["UK", "EUROPE", "GLOBAL"],
    "FR": ["EU", "EUROPE", "GLOBAL"],
    "DE": ["EU", "EUROPE", "GLOBAL"],
    "ES": ["EU", "EUROPE", "GLOBAL"],
    "IT": ["EU", "EUROPE", "GLOBAL"],
    "NL": ["EU", "EUROPE", "GLOBAL"],
    "PL": ["EU", "EUROPE", "GLOBAL"],
    "IE": ["EU", "EUROPE", "GLOBAL"],
    "US": ["NA", "AMERICAS", "GLOBAL"],
    "CA": ["NA", "AMERICAS", "GLOBAL"],
    "MX": ["NA", "AMERICAS", "GLOBAL"],
    "BR": ["AMERICAS", "GLOBAL"],
    "IN": ["ASIA", "GLOBAL"],
    "CN": ["ASIA", "GLOBAL"],
    "JP": ["ASIA", "GLOBAL"],
    "AU": ["OCEANIA", "GLOBAL"],
}

# Region tokens that never map to a country (caller passes a group directly).
REGION_GROUPS: set[str] = {
    "EU", "EUROPE", "NA", "AMERICAS", "ASIA", "OCEANIA", "AFRICA", "GLOBAL", "UK",
}


def _norm_region(token: str) -> str:
    return (token or "").strip().upper()


def normalise_region(token: str) -> str:
    """Resolve aliases to a canonical country code or group token."""
    n = _norm_region(token)
    if not n:
        return "GLOBAL"
    return COUNTRY_ALIASES.get(n, n)


def region_chain(token: str) -> List[str]:
    """Build the ordered fallback chain for a request region.

    Index 0 is the most-preferred match (exact); subsequent entries are
    progressively broader. The chain always terminates at GLOBAL so a
    library that only stocks Global factors still resolves.

    The raw (upper-cased) input token is always tried first so a factor
    seeded with the colloquial label ("UK") still counts as an exact match
    when the caller passes "UK". The canonical alias ("GB") and the
    hierarchical fallbacks come after.
    """
    raw = _norm_region(token) or "GLOBAL"
    canonical = normalise_region(token)

    chain: List[str] = [raw]
    if canonical != raw:
        chain.append(canonical)

    # If the canonical is a country we know, append its group/continent/global.
    if canonical in REGION_HIERARCHY:
        chain.extend(REGION_HIERARCHY[canonical])

    if "GLOBAL" not in chain:
        chain.append("GLOBAL")

    # Dedupe preserving order.
    seen, out = set(), []
    for r in chain:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


# ---- Subcategory knowledge --------------------------------------------------

def _norm_sub(token: str) -> str:
    return (token or "").strip().lower()


def subcategory_candidates(subcategory: str) -> List[Tuple[str, str]]:
    """Yield (subcategory_token, match_quality) tuples to try in order.

    Strategy:
    - exact: lower-cased original
    - parent_fallback: if the original looks like a "name_specifier" (e.g.
      "diesel_generator_50kva"), strip the trailing token and retry.
    """
    base = _norm_sub(subcategory)
    out: list[tuple[str, str]] = [(base, "exact")]
    parts = base.split("_")
    while len(parts) > 2:
        parts = parts[:-1]
        out.append(("_".join(parts), "parent_fallback"))
    return out


# ---- Temporal validity ------------------------------------------------------

def _as_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def temporal_quality(factor: models.EmissionFactor, as_of: date) -> str:
    """Grade a factor's temporal applicability for the requested date.

    - current: valid_from <= as_of <= valid_to (or valid_to is open)
    - expired: valid_to < as_of
    - future: valid_from > as_of (rare; pre-published factors)
    """
    vf = _as_date(factor.valid_from)
    vt = _as_date(factor.valid_to)
    if vf and vf > as_of:
        return "future"
    if vt and vt < as_of:
        return "expired"
    return "current"


# ---- Result type ------------------------------------------------------------

@dataclass
class MatchQuality:
    region: str            # exact | region_group_fallback | continent_fallback | global_fallback
    subcategory: str       # exact | parent_fallback
    temporal: str          # current | expired | future
    region_step: int       # how many steps down the chain we went (0 = exact)


@dataclass
class ResolvedFactor:
    factor: models.EmissionFactor
    quality: MatchQuality

    def to_audit(self) -> dict:
        """Compact audit payload for persistence on the event row."""
        return {
            "region_match": self.quality.region,
            "subcategory_match": self.quality.subcategory,
            "temporal_match": self.quality.temporal,
        }


# ---- Resolver ---------------------------------------------------------------

def _grade_region(step_index: int, chain: List[str]) -> str:
    if step_index == 0:
        return "exact"
    token = chain[step_index]
    if token == "GLOBAL":
        return "global_fallback"
    if token in {"EUROPE", "AMERICAS", "ASIA", "OCEANIA", "AFRICA"}:
        return "continent_fallback"
    return "region_group_fallback"


def resolve(
    db: Session,
    category: str,
    subcategory: str,
    region: str,
    standard: Optional[str] = None,
    as_of: Optional[date] = None,
) -> Optional[ResolvedFactor]:
    """Find the best EmissionFactor row for the request, with grading.

    Returns None only if absolutely nothing matches the (category, subcategory*)
    combination across any region   — at which point the caller should raise.
    """
    as_of = as_of or date.today()
    chain = region_chain(region)

    # Pre-build the subcategory candidates once.
    sub_candidates = subcategory_candidates(subcategory)

    # We iterate by region first (closest first), then by subcategory quality
    # (exact before parent_fallback). This means a parent-fallback factor in
    # the exact country beats an exact-subcategory Global factor   — which is
    # almost always what auditors want (regional accuracy > taxonomy precision).
    base_q = db.query(models.EmissionFactor).filter(
        models.EmissionFactor.category == category,
        models.EmissionFactor.is_active == True,
    )
    if standard:
        base_q = base_q.filter(models.EmissionFactor.standard == standard)

    best: Optional[ResolvedFactor] = None
    best_rank: tuple = ()  # lexicographic; smaller = better

    for region_idx, region_token in enumerate(chain):
        for sub_token, sub_quality in sub_candidates:
            rows = (
                base_q.filter(
                    models.EmissionFactor.subcategory == sub_token,
                    func.upper(models.EmissionFactor.region) == region_token,
                )
                .order_by(
                    models.EmissionFactor.valid_from.desc(),
                    models.EmissionFactor.version.desc(),
                )
                .all()
            )
            if not rows:
                continue

            # Pick the best row in this bucket: prefer current → future →
            # expired, and within each, the most recent valid_from + highest
            # version (already ordered by query).
            rows_graded = [(r, temporal_quality(r, as_of)) for r in rows]
            ordering = {"current": 0, "future": 1, "expired": 2}
            rows_graded.sort(key=lambda x: ordering.get(x[1], 3))
            row, t_quality = rows_graded[0]

            mq = MatchQuality(
                region=_grade_region(region_idx, chain),
                subcategory=sub_quality,
                temporal=t_quality,
                region_step=region_idx,
            )
            # Composite rank: lower is better.
            #   region_step → primary axis (proximity)
            #   sub_rank    → exact (0) < parent_fallback (1)
            #   temp_rank   → current (0) < future (1) < expired (2)
            rank = (
                region_idx,
                0 if sub_quality == "exact" else 1,
                ordering[t_quality],
            )
            if best is None or rank < best_rank:
                best = ResolvedFactor(factor=row, quality=mq)
                best_rank = rank
                # Short-circuit: a perfect match can't be beaten.
                if rank == (0, 0, 0):
                    return best

    return best
