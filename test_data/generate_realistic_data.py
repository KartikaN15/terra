"""
Realistic Synthetic Data Generator
Generates 100+ film/TV productions with statistically realistic carbon footprints
based on SPA, BAFTA albert, and Netflix ESG benchmarks.
"""

import csv
import random
import uuid
from decimal import Decimal
from datetime import datetime, timedelta

random.seed(42)

# ============================================================================
# REAL BENCHMARKS (from web research)
# ============================================================================

FEATURE_BENCHMARKS = {
    "FEATURE": {
        "TENTPOLE": {"total_tco2e": 3370, "per_day": 33, "fuel_pct": 0.48, "travel_pct": 0.24, "energy_pct": 0.22, "accom_pct": 0.06},
        "LARGE":    {"total_tco2e": 1081, "per_day": 22, "fuel_pct": 0.50, "travel_pct": 0.20, "energy_pct": 0.22, "accom_pct": 0.08},
        "MEDIUM":   {"total_tco2e": 769,  "per_day": 19, "fuel_pct": 0.45, "travel_pct": 0.25, "energy_pct": 0.22, "accom_pct": 0.08},
        "SMALL":    {"total_tco2e": 391,  "per_day": 16, "fuel_pct": 0.42, "travel_pct": 0.28, "energy_pct": 0.22, "accom_pct": 0.08},
    },
    "TV_SERIES": {
        "DRAMA_1H":        {"per_episode": 77,  "fuel_pct": 0.35, "travel_pct": 0.30, "energy_pct": 0.25, "accom_pct": 0.10},
        "SITCOM_SINGLE":   {"per_episode": 26,  "fuel_pct": 0.25, "travel_pct": 0.15, "energy_pct": 0.45, "accom_pct": 0.15},
        "SITCOM_MULTI":    {"per_episode": 18,  "fuel_pct": 0.15, "travel_pct": 0.10, "energy_pct": 0.55, "accom_pct": 0.20},
        "UNSCRIPTED":      {"per_episode": 13,  "fuel_pct": 0.18, "travel_pct": 0.55, "energy_pct": 0.17, "accom_pct": 0.10},
        "REALITY":         {"per_episode": 16,  "fuel_pct": 0.20, "travel_pct": 0.40, "energy_pct": 0.25, "accom_pct": 0.15},
    }
}

# Genre → benchmark mapping
GENRE_MAP = {
    "ACTION": ("FEATURE", "LARGE", 0.9),
    "COMEDY": ("TV_SERIES", "SITCOM_MULTI", 0.7),
    "DRAMA": ("TV_SERIES", "DRAMA_1H", 0.85),
    "HORROR": ("FEATURE", "MEDIUM", 0.6),
    "SCI_FI": ("FEATURE", "TENTPOLE", 0.95),
    "DOCUMENTARY": ("TV_SERIES", "UNSCRIPTED", 0.8),
    "REALITY": ("TV_SERIES", "REALITY", 0.9),
    "ANIMATION": ("FEATURE", "MEDIUM", 0.5),
    "ROMANCE": ("FEATURE", "SMALL", 0.5),
    "THRILLER": ("FEATURE", "MEDIUM", 0.7),
    "FANTASY": ("FEATURE", "LARGE", 0.85),
    "CRIME": ("TV_SERIES", "DRAMA_1H", 0.75),
}

BUDGET_BANDS = ["UNDER_1M", "_1M_TO_5M", "_5M_TO_10M", "_10M_TO_50M", "OVER_50M"]
BUDGET_MULTIPLIERS = {
    "UNDER_1M": 0.3, "_1M_TO_5M": 0.6, "_5M_TO_10M": 1.0,
    "_10M_TO_50M": 2.5, "OVER_50M": 5.0
}

VFX_MULTIPLIERS = {
    "NONE": 0.9, "LOW": 1.0, "MEDIUM": 1.15, "HIGH": 1.4, "EXTREME": 1.8
}

REGION_GRID = {
    "UK": 0.207, "US": 0.390, "EU": 0.278, "CA": 0.130, "AU": 0.550,
    "DE": 0.380, "FR": 0.060, "NZ": 0.130, "ES": 0.180, "IE": 0.260,
}

# ============================================================================
# GENERATOR
# ============================================================================

def generate_productions(n=100):
    productions = []
    genres = list(GENRE_MAP.keys())
    regions = list(REGION_GRID.keys())
    vfx_levels = ["NONE", "LOW", "MEDIUM", "HIGH", "EXTREME"]

    for i in range(n):
        genre = random.choice(genres)
        ptype, bkey, genre_conf = GENRE_MAP[genre]
        benchmark = FEATURE_BENCHMARKS[ptype][bkey]

        # Budget band strongly correlates with genre
        if ptype == "FEATURE":
            if genre in ["SCI_FI", "ACTION", "FANTASY"]:
                budget_band = random.choices(BUDGET_BANDS, weights=[5, 15, 25, 35, 20])[0]
            elif genre in ["HORROR", "THRILLER", "ANIMATION"]:
                budget_band = random.choices(BUDGET_BANDS, weights=[10, 30, 30, 20, 10])[0]
            else:
                budget_band = random.choices(BUDGET_BANDS, weights=[20, 35, 25, 15, 5])[0]
        else:
            # TV series
            if genre in ["DRAMA", "CRIME"]:
                budget_band = random.choices(["UNDER_1M", "_1M_TO_5M", "_5M_TO_10M"], weights=[20, 50, 30])[0]
            elif genre in ["COMEDY", "REALITY"]:
                budget_band = random.choices(["UNDER_1M", "_1M_TO_5M"], weights=[40, 60])[0]
            else:
                budget_band = random.choices(["UNDER_1M", "_1M_TO_5M", "_5M_TO_10M"], weights=[30, 50, 20])[0]

        # Episodes and runtime
        if ptype == "FEATURE":
            episodes = 1
            runtime = random.randint(85, 150)
            shoot_days = int(benchmark.get("per_day", 20) * 15 + random.gauss(0, 8))
            if shoot_days < 10: shoot_days = 10
        else:
            if genre in ["COMEDY"]:
                episodes = random.randint(6, 24)
                runtime = random.randint(20, 30)
                shoot_days = int(episodes * 1.5 + random.gauss(0, 3))
            elif genre in ["DRAMA", "CRIME"]:
                episodes = random.randint(4, 12)
                runtime = random.randint(42, 60)
                shoot_days = int(episodes * 8 + random.gauss(0, 10))
            else:
                episodes = random.randint(6, 16)
                runtime = random.randint(22, 45)
                shoot_days = int(episodes * 2 + random.gauss(0, 5))

        # VFX correlates with genre
        if genre in ["SCI_FI", "ACTION", "FANTASY", "ANIMATION"]:
            vfx = random.choices(vfx_levels, weights=[2, 5, 15, 35, 43])[0]
        elif genre in ["HORROR", "THRILLER"]:
            vfx = random.choices(vfx_levels, weights=[10, 20, 35, 25, 10])[0]
        elif genre == "DOCUMENTARY":
            vfx = random.choices(vfx_levels, weights=[50, 30, 15, 4, 1])[0]
        else:
            vfx = random.choices(vfx_levels, weights=[30, 35, 25, 8, 2])[0]

        # Crew count correlates with budget and shoot days
        base_crew = {"UNDER_1M": 15, "_1M_TO_5M": 35, "_5M_TO_10M": 60, "_10M_TO_50M": 100, "OVER_50M": 180}[budget_band]
        crew_count = int(base_crew + random.gauss(0, base_crew * 0.15))
        cast_count = max(2, int(crew_count * random.uniform(0.08, 0.18)))

        region = random.choice(regions)

        prod = {
            "project_id": str(uuid.uuid4()),
            "title": f"Project {i+1:03d} ({genre.title()})",
            "type": ptype,
            "genre": genre,
            "budget_band": budget_band,
            "runtime_min": runtime,
            "episodes": episodes,
            "shoot_days": max(1, shoot_days),
            "locations": [region],
            "cast_count": cast_count,
            "crew_count": crew_count,
            "vfx_intensity": vfx,
            "status": random.choice(["WRAPPED", "PRODUCTION", "POST_PRODUCTION"]),
            "primary_region": region,
            "_benchmark": benchmark,
            "_budget_mult": BUDGET_MULTIPLIERS[budget_band],
            "_vfx_mult": VFX_MULTIPLIERS[vfx],
        }
        productions.append(prod)

    return productions


def generate_events_for_production(prod):
    """Generate realistic events with proper category splits."""
    benchmark = prod["_benchmark"]
    budget_mult = prod["_budget_mult"]
    vfx_mult = prod["_vfx_mult"]

    if prod["type"] == "FEATURE":
        base_tco2e = benchmark["total_tco2e"] * budget_mult * random.uniform(0.85, 1.15)
    else:
        base_tco2e = benchmark["per_episode"] * prod["episodes"] * budget_mult * random.uniform(0.85, 1.15)

    # VFX multiplier mainly affects post/VFX category
    total_kgco2e = base_tco2e * 1000

    splits = {
        "fuel": benchmark["fuel_pct"] * random.uniform(0.9, 1.1),
        "travel": benchmark["travel_pct"] * random.uniform(0.9, 1.1),
        "energy": benchmark["energy_pct"] * random.uniform(0.9, 1.1),
        "accom": benchmark["accom_pct"] * random.uniform(0.9, 1.1),
    }
    # Normalize to sum to ~0.95 (leaving room for waste/materials/catering)
    total_split = sum(splits.values())
    for k in splits:
        splits[k] /= total_split
        splits[k] *= 0.92

    # Remaining ~8% for waste, materials, catering, water
    waste_pct = 0.03
    materials_pct = 0.025 if prod["type"] == "FEATURE" else 0.01
    catering_pct = 0.02
    water_pct = 0.005
    vfx_post_pct = 0.0

    if prod["vfx_intensity"] in ["HIGH", "EXTREME"]:
        vfx_post_pct = 0.05 * (VFX_MULTIPLIERS[prod["vfx_intensity"]] - 1.0)
        # Reduce others proportionally
        for k in splits:
            splits[k] *= (1 - vfx_post_pct)

    grid_factor = REGION_GRID.get(prod["primary_region"], 0.207)
    events = []

    def add_event(phase, scope, category, subcategory, value, unit, factor_val, source_type, ref):
        kg = Decimal(str(value)) * Decimal(str(factor_val))
        events.append({
            "event_id": str(uuid.uuid4()),
            "production_id": prod["project_id"],
            "phase": phase,
            "scope": scope,
            "category": category,
            "subcategory": subcategory,
            "value": round(Decimal(str(value)), 4),
            "unit": unit,
            "kgco2e": round(kg, 4),
            "confidence_tier": "TIER_1_DIRECT" if source_type == "MANUAL_ENTRY" else "TIER_2_BENCHMARK",
            "confidence_score": round(Decimal(str(random.uniform(0.88, 0.98))), 2) if source_type == "MANUAL_ENTRY" else round(Decimal(str(random.uniform(0.70, 0.85))), 2),
            "source_type": source_type,
            "source_reference": ref,
            "grid_region": prod["primary_region"],
            "recorded_at": (datetime(2024, random.randint(1, 12), random.randint(1, 28))).isoformat(),
        })

    # FUEL
    fuel_kg = float(total_kgco2e) * splits["fuel"]
    diesel_l = fuel_kg * 0.75 / 2.546
    add_event("PRODUCTION", "SCOPE_1", "ENERGY", "diesel_generator", round(diesel_l, 1), "LITRES", 2.546, "MANUAL_ENTRY", "gen_log_001")
    if random.random() > 0.4:
        hvo_l = fuel_kg * 0.20 / 0.195
        add_event("PRODUCTION", "SCOPE_1", "ENERGY", "hvo_fuel", round(hvo_l, 1), "LITRES", 0.195, "MANUAL_ENTRY", "hvo_delivery")
    petrol_l = fuel_kg * 0.05 / 2.136
    add_event("PRODUCTION", "SCOPE_1", "TRANSPORT", "petrol_vehicle", round(petrol_l, 1), "LITRES", 2.136, "INVOICE_OCR", "fleet_receipt")

    # ENERGY
    energy_kg = float(total_kgco2e) * splits["energy"]
    studio_kwh = energy_kg * 0.70 / grid_factor
    add_event("PRODUCTION", "SCOPE_2", "ENERGY", "grid_electricity", round(studio_kwh, 1), "KWH", grid_factor, "MANUAL_ENTRY", "elec_bill")
    office_kwh = energy_kg * 0.25 / grid_factor
    add_event("PRE_PRODUCTION", "SCOPE_2", "ENERGY", "grid_electricity", round(office_kwh, 1), "KWH", grid_factor, "MANUAL_ENTRY", "office_bill")
    if random.random() > 0.5:
        gas_kwh = energy_kg * 0.05 / 0.182
        add_event("PRODUCTION", "SCOPE_1", "ENERGY", "natural_gas", round(gas_kwh, 1), "KWH", 0.182, "MANUAL_ENTRY", "gas_bill")

    # TRAVEL
    travel_kg = float(total_kgco2e) * splits["travel"]
    short_km = travel_kg * 0.30 / 0.158
    add_event("PRE_PRODUCTION", "SCOPE_3", "TRANSPORT", "short_haul_flight", round(short_km, 1), "KM", 0.158, "INVOICE_OCR", "travel_dom")
    long_km = travel_kg * 0.55 / 0.195
    add_event("PRE_PRODUCTION", "SCOPE_3", "TRANSPORT", "long_haul_flight", round(long_km, 1), "KM", 0.195, "INVOICE_OCR", "travel_intl")
    coach_km = travel_kg * 0.10 / 0.027
    add_event("PRODUCTION", "SCOPE_3", "TRANSPORT", "coach", round(coach_km, 1), "KM", 0.027, "INVOICE_OCR", "transport_contract")
    car_km = travel_kg * 0.05 / 0.171
    add_event("PRODUCTION", "SCOPE_3", "TRANSPORT", "medium_car_diesel", round(car_km, 1), "KM", 0.171, "INVOICE_OCR", "vehicle_log")

    # ACCOMMODATION
    accom_kg = float(total_kgco2e) * splits["accom"]
    hotel_nights = accom_kg / 10.4
    add_event("PRODUCTION", "SCOPE_3", "ACCOMMODATION", "hotel", round(hotel_nights, 1), "NIGHTS", 10.4, "INVOICE_OCR", "hotel_booking")

    # WASTE
    waste_kg = float(total_kgco2e) * waste_pct
    add_event("PRODUCTION", "SCOPE_3", "WASTE", "landfill_general", round(waste_kg * 0.40 / 0.500, 1), "KG", 0.500, "MANUAL_ENTRY", "waste_ticket")
    add_event("PRODUCTION", "SCOPE_3", "WASTE", "recycling_mixed", round(waste_kg * 0.50 / 0.020, 1), "KG", 0.020, "MANUAL_ENTRY", "recycling_cert")
    add_event("PRODUCTION", "SCOPE_3", "WASTE", "compost", round(waste_kg * 0.10 / 0.010, 1), "KG", 0.010, "MANUAL_ENTRY", "compost_receipt")

    # MATERIALS
    if materials_pct > 0:
        mat_kg = float(total_kgco2e) * materials_pct
        add_event("PRE_PRODUCTION", "SCOPE_3", "MATERIALS", "lumber_general", round(mat_kg * 0.60 / 0.50, 1), "KG", 0.50, "INVOICE_OCR", "set_construction")
        add_event("PRE_PRODUCTION", "SCOPE_3", "MATERIALS", "steel", round(mat_kg * 0.40 / 1.35, 1), "KG", 1.35, "INVOICE_OCR", "scaffolding")

    # CATERING
    cat_kg = float(total_kgco2e) * catering_pct
    add_event("PRODUCTION", "SCOPE_3", "CATERING", "beef", round(cat_kg * 0.30 / 60.0, 2), "KG", 60.0, "INVOICE_OCR", "catering_inv")
    add_event("PRODUCTION", "SCOPE_3", "CATERING", "chicken", round(cat_kg * 0.40 / 6.1, 2), "KG", 6.1, "INVOICE_OCR", "catering_inv")
    add_event("PRODUCTION", "SCOPE_3", "CATERING", "vegetables", round(cat_kg * 0.30 / 0.5, 2), "KG", 0.5, "INVOICE_OCR", "catering_inv")

    # WATER
    water_kg = float(total_kgco2e) * water_pct
    add_event("PRODUCTION", "SCOPE_3", "WATER", "water_supply", round(water_kg / 0.150, 1), "M3", 0.150, "INVOICE_OCR", "water_bill")

    # POST/VFX
    if vfx_post_pct > 0:
        vfx_kg = float(total_kgco2e) * vfx_post_pct
        add_event("POST_PRODUCTION", "SCOPE_3", "POST_VFX", "vfx_render_farm", round(vfx_kg / grid_factor, 1), "KWH", grid_factor, "INVOICE_OCR", "render_bill")

    return events


def main():
    print("Generating realistic production dataset...")
    productions = generate_productions(n=100)
    all_events = []
    for p in productions:
        all_events.extend(generate_events_for_production(p))

    # Write productions
    with open("sample_productions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["production_id", "title", "type", "genre", "budget_band", "runtime_min",
                         "episodes", "shoot_days", "locations", "cast_count", "crew_count",
                         "vfx_intensity", "status", "primary_region"])
        for p in productions:
            writer.writerow([
                p["project_id"], p["title"], p["type"], p["genre"], p["budget_band"],
                p["runtime_min"], p["episodes"], p["shoot_days"],
                "|".join(p["locations"]), p["cast_count"], p["crew_count"],
                p["vfx_intensity"], p["status"], p["primary_region"]
            ])

    # Write events
    with open("sample_activity_events.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "event_id", "production_id", "phase", "scope", "category", "subcategory",
            "value", "unit", "kgco2e", "confidence_tier", "confidence_score",
            "source_type", "source_reference", "grid_region", "recorded_at"
        ])
        for e in all_events:
            writer.writerow([
                e["event_id"], e["production_id"], e["phase"], e["scope"], e["category"],
                e["subcategory"], e["value"], e["unit"], e["kgco2e"],
                e["confidence_tier"], e["confidence_score"], e["source_type"],
                e["source_reference"], e["grid_region"], e["recorded_at"]
            ])

    # Validation report
    print(f"\nGenerated {len(productions)} productions, {len(all_events)} events")
    total_co2 = sum(float(e["kgco2e"]) for e in all_events) / 1000
    print(f"Total synthetic footprint: {total_co2:,.1f} tCO2e")

    # Per-genre averages
    from collections import defaultdict
    genre_totals = defaultdict(float)
    genre_counts = defaultdict(int)
    for p in productions:
        pid = p["project_id"]
        t = sum(float(e["kgco2e"]) for e in all_events if e["production_id"] == pid) / 1000
        if p["type"] == "TV_SERIES":
            t = t / p["episodes"]
        genre_totals[p["genre"]] += t
        genre_counts[p["genre"]] += 1

    print("\nPer-genre average (tCO2e per episode or film):")
    for g in sorted(genre_totals.keys()):
        avg = genre_totals[g] / genre_counts[g]
        print(f"  {g:<15}: {avg:>8.1f}  (n={genre_counts[g]})")

    print("\nFiles written:")
    print("  - sample_productions.csv")
    print("  - sample_activity_events.csv")


if __name__ == "__main__":
    main()
