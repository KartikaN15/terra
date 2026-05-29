"""
Scope Auto-Classifier
GHG Protocol rules for Scope 1 / 2 / 3 classification.

FALLBACK ONLY. The authoritative source of scope is the matched
EmissionFactor.scope. Use this classifier only when no factor is available
(e.g. forecast-only events or imputed categories without a factor lookup).
"""

SCOPE_1_RULES = [
    "diesel_generator", "natural_gas", "propane", "company_vehicle",
    "petrol_vehicle", "hvo_fuel", "refrigerant", "lpg", "kerosene",
]

SCOPE_2_RULES = [
    "grid_electricity", "purchased_heat", "purchased_steam", "purchased_cooling",
]

SCOPE_3_RULES = [
    "commercial_air_travel", "hotel", "landfill", "recycling", "compost",
    "catering", "cloud", "vfx", "freight", "commuting", "materials",
    "water_supply", "wastewater",
]


def classify_scope(subcategory: str) -> str:
    sub = subcategory.lower()
    for pattern in SCOPE_1_RULES:
        if pattern in sub:
            return "SCOPE_1"
    for pattern in SCOPE_2_RULES:
        if pattern in sub:
            return "SCOPE_2"
    for pattern in SCOPE_3_RULES:
        if pattern in sub:
            return "SCOPE_3"
    # Heuristic fallback
    if "electricity" in sub and "generator" not in sub:
        return "SCOPE_2"
    if any(f in sub for f in ["diesel", "petrol", "gas", "propane", "hvo"]):
        return "SCOPE_1"
    return "SCOPE_3"
