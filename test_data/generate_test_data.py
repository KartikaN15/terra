"""
Synthetic Test Data Generator for Production Sustainability Platform
Uses real industry benchmarks (SPA, BAFTA albert, Netflix ESG) to create
realistic production + activity event data for backend testing.
"""

import csv
import random
import uuid
from decimal import Decimal
from datetime import datetime, timedelta

random.seed(42)

# ============================================================================
# REAL INDUSTRY BENCHMARKS (from web research)
# ============================================================================

BENCHMARKS = {
    # SPA / Green Production Alliance (2021)
    ("FEATURE", "TENTPOLE"): 3370,      # $70M+ budget
    ("FEATURE", "LARGE"): 1081,         # $40-70M
    ("FEATURE", "MEDIUM"): 769,         # $20-40M
    ("FEATURE", "SMALL"): 391,          # <$20M
    ("TV_SERIES", "DRAMA_1H"): 77,      # per episode
    ("TV_SERIES", "SITCOM_SINGLE"): 26, # per episode
    ("TV_SERIES", "SITCOM_MULTI"): 18,  # per episode
    ("TV_SERIES", "UNSCRIPTED"): 13,    # per episode
}

# Category breakdowns by production type
CATEGORY_SPLIT = {
    "FEATURE": {"fuel": 0.48, "travel": 0.24, "energy": 0.22, "accommodation": 0.06},
    "TV_DRAMA": {"fuel": 0.35, "travel": 0.30, "energy": 0.25, "accommodation": 0.10},
    "TV_SITCOM": {"fuel": 0.20, "travel": 0.15, "energy": 0.49, "accommodation": 0.16},
    "TV_UNSCRIPTED": {"fuel": 0.18, "travel": 0.61, "energy": 0.15, "accommodation": 0.06},
}

# Emission factors (DEFRA 2024 approximations)
FACTORS = {
    "diesel_generator": Decimal("2.546"),      # kgCO2e/L
    "petrol_vehicle": Decimal("2.136"),        # kgCO2e/L
    "hvo_fuel": Decimal("0.195"),              # kgCO2e/L
    "natural_gas": Decimal("0.182"),           # kgCO2e/kWh
    "grid_electricity_uk": Decimal("0.207"),   # kgCO2e/kWh
    "grid_electricity_us": Decimal("0.390"),   # kgCO2e/kWh (US average)
    "short_haul_flight": Decimal("0.158"),     # kgCO2e/km
    "long_haul_flight": Decimal("0.195"),      # kgCO2e/km
    "hotel_night": Decimal("10.4"),            # kgCO2e/room/night
    "landfill_waste": Decimal("0.500"),        # kgCO2e/kg
    "recycling_mixed": Decimal("0.020"),       # kgCO2e/kg
    "compost_waste": Decimal("0.010"),         # kgCO2e/kg
    "water_supply": Decimal("0.150"),          # kgCO2e/m3
    "beef": Decimal("60.0"),                   # kgCO2e/kg
    "chicken": Decimal("6.1"),                 # kgCO2e/kg
    "vegetables": Decimal("0.5"),              # kgCO2e/kg
    "lumber": Decimal("0.50"),                 # kgCO2e/kg
    "steel": Decimal("1.35"),                  # kgCO2e/kg
    "medium_car_diesel": Decimal("0.171"),     # kgCO2e/km
    "coach": Decimal("0.027"),                 # kgCO2e/km
}

# ============================================================================
# PRODUCTION DEFINITIONS
# ============================================================================

PRODUCTIONS = [
    {
        "id": str(uuid.uuid4()),
        "title": "The Midnight Heist",
        "type": "FEATURE",
        "genre": "ACTION",
        "budget_band": "_10M_TO_50M",
        "runtime_min": 128,
        "episodes": 1,
        "shoot_days": 52,
        "locations": ["London, UK", "Prague, Czech Republic"],
        "cast_count": 12,
        "crew_count": 145,
        "vfx_intensity": "HIGH",
        "status": "WRAPPED",
        "benchmark_type": "FEATURE",
        "benchmark_size": "LARGE",
        "primary_region": "UK",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Crown & Dagger Season 3",
        "type": "TV_SERIES",
        "genre": "DRAMA",
        "budget_band": "_5M_TO_10M",
        "runtime_min": 58,
        "episodes": 8,
        "shoot_days": 96,
        "locations": ["Bath, UK", "Bristol Studios"],
        "cast_count": 18,
        "crew_count": 85,
        "vfx_intensity": "MEDIUM",
        "status": "POST_PRODUCTION",
        "benchmark_type": "TV_DRAMA",
        "benchmark_size": "DRAMA_1H",
        "primary_region": "UK",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Coastal Kitchen",
        "type": "TV_SERIES",
        "genre": "REALITY",
        "budget_band": "UNDER_1M",
        "runtime_min": 24,
        "episodes": 12,
        "shoot_days": 36,
        "locations": ["Cornwall, UK"],
        "cast_count": 4,
        "crew_count": 22,
        "vfx_intensity": "NONE",
        "status": "WRAPPED",
        "benchmark_type": "TV_UNSCRIPTED",
        "benchmark_size": "UNSCRIPTED",
        "primary_region": "UK",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "The Last Colony",
        "type": "FEATURE",
        "genre": "SCI_FI",
        "budget_band": "OVER_50M",
        "runtime_min": 142,
        "episodes": 1,
        "shoot_days": 78,
        "locations": ["Vancouver, Canada", "Auckland, NZ"],
        "cast_count": 8,
        "crew_count": 220,
        "vfx_intensity": "EXTREME",
        "status": "PRODUCTION",
        "benchmark_type": "FEATURE",
        "benchmark_size": "TENTPOLE",
        "primary_region": "US",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Laugh Track Live",
        "type": "TV_SERIES",
        "genre": "COMEDY",
        "budget_band": "_1M_TO_5M",
        "runtime_min": 22,
        "episodes": 22,
        "shoot_days": 55,
        "locations": ["Manchester Studios"],
        "cast_count": 6,
        "crew_count": 45,
        "vfx_intensity": "NONE",
        "status": "PRODUCTION",
        "benchmark_type": "TV_SITCOM",
        "benchmark_size": "SITCOM_MULTI",
        "primary_region": "UK",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Bloodline: Origins",
        "type": "TV_SERIES",
        "genre": "DRAMA",
        "budget_band": "_5M_TO_10M",
        "runtime_min": 52,
        "episodes": 6,
        "shoot_days": 72,
        "locations": ["Glasgow, UK", "Edinburgh, UK"],
        "cast_count": 14,
        "crew_count": 92,
        "vfx_intensity": "LOW",
        "status": "WRAPPED",
        "benchmark_type": "TV_DRAMA",
        "benchmark_size": "DRAMA_1H",
        "primary_region": "UK",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Desert Wind",
        "type": "FEATURE",
        "genre": "WESTERN",
        "budget_band": "_20M_TO_40M",
        "runtime_min": 115,
        "episodes": 1,
        "shoot_days": 48,
        "locations": ["Almeria, Spain", "Tabernas Desert"],
        "cast_count": 10,
        "crew_count": 110,
        "vfx_intensity": "MEDIUM",
        "status": "PRE_PRODUCTION",
        "benchmark_type": "FEATURE",
        "benchmark_size": "MEDIUM",
        "primary_region": "EU",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Deep Blue Mystery",
        "type": "TV_SERIES",
        "genre": "CRIME",
        "budget_band": "_1M_TO_5M",
        "runtime_min": 45,
        "episodes": 4,
        "shoot_days": 28,
        "locations": ["Brighton, UK"],
        "cast_count": 9,
        "crew_count": 38,
        "vfx_intensity": "LOW",
        "status": "WRAPPED",
        "benchmark_type": "TV_DRAMA",
        "benchmark_size": "DRAMA_1H",
        "primary_region": "UK",
    },
]

# ============================================================================
# EVENT GENERATOR
# ============================================================================

def generate_events_for_production(prod):
    """Generate realistic activity events for a production."""
    events = []
    base_tco2e = BENCHMARKS.get((prod["benchmark_type"], prod["benchmark_size"]), 500)
    
    # For TV series, multiply by episodes
    if prod["type"] == "TV_SERIES":
        total_tco2e = base_tco2e * prod["episodes"]
    else:
        total_tco2e = base_tco2e
    
    # Add ±15% noise
    total_tco2e = Decimal(str(total_tco2e)) * Decimal(str(random.uniform(0.85, 1.15)))
    total_kgco2e = total_tco2e * Decimal("1000")
    
    splits = CATEGORY_SPLIT.get(prod["benchmark_type"], CATEGORY_SPLIT["TV_DRAMA"])
    
    grid_factor = FACTORS["grid_electricity_uk"] if prod["primary_region"] == "UK" else FACTORS["grid_electricity_us"]
    
    # Use float for synthetic generation math
    total_kg_f = float(total_kgco2e)
    
    # --- FUEL EVENTS (Scope 1) ---
    fuel_kgco2e = total_kg_f * splits["fuel"]
    
    # Diesel generators (main production power)
    diesel_litres = fuel_kgco2e * 0.75 / float(FACTORS["diesel_generator"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_1", "ENERGY", "diesel_generator", 
                             round(diesel_litres, 1), "LITRES", FACTORS["diesel_generator"],
                             "TIER_1", "generator_log_001", "UK"))
    
    # HVO (sustainable alternative, ~20% of fuel)
    if random.random() > 0.3:
        hvo_litres = float(fuel_kgco2e) * 0.20 / float(FACTORS["hvo_fuel"])
        events.append(make_event(prod, "PRODUCTION", "SCOPE_1", "ENERGY", "hvo_fuel",
                                 round(hvo_litres, 1), "LITRES", FACTORS["hvo_fuel"],
                                 "TIER_1", "fuel_delivery_hvo", prod["primary_region"]))
    
    # Petrol for crew vehicles
    petrol_litres = float(fuel_kgco2e) * 0.05 / float(FACTORS["petrol_vehicle"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_1", "TRANSPORT", "petrol_vehicle",
                             round(petrol_litres, 1), "LITRES", FACTORS["petrol_vehicle"],
                             "TIER_2", "fleet_fuel_receipt", prod["primary_region"]))
    
    # --- ENERGY EVENTS (Scope 2) ---
    energy_kgco2e = total_kg_f * splits["energy"]
    
    # Studio / location electricity
    studio_kwh = float(energy_kgco2e) * 0.70 / float(grid_factor)
    events.append(make_event(prod, "PRODUCTION", "SCOPE_2", "ENERGY", "grid_electricity",
                             round(studio_kwh, 1), "KWH", grid_factor,
                             "TIER_1", "electricity_bill_studio", prod["primary_region"]))
    
    # Office / basecamp electricity
    office_kwh = float(energy_kgco2e) * 0.25 / float(grid_factor)
    events.append(make_event(prod, "PRE_PRODUCTION", "SCOPE_2", "ENERGY", "grid_electricity",
                             round(office_kwh, 1), "KWH", grid_factor,
                             "TIER_1", "electricity_bill_office", prod["primary_region"]))
    
    # Natural gas heating (if UK winter shoot)
    if prod["primary_region"] == "UK" and random.random() > 0.4:
        gas_kwh = float(energy_kgco2e) * 0.05 / float(FACTORS["natural_gas"])
        events.append(make_event(prod, "PRODUCTION", "SCOPE_1", "ENERGY", "natural_gas",
                                 round(gas_kwh, 1), "KWH", FACTORS["natural_gas"],
                                 "TIER_1", "gas_bill_studio", "UK"))
    
    # --- TRAVEL EVENTS (Scope 3) ---
    travel_kgco2e = total_kg_f * splits["travel"]
    
    # Flights (cast + key crew)
    flight_kgco2e = travel_kgco2e * 0.65
    # Short-haul flights (within Europe/UK)
    short_haul_km = float(flight_kgco2e) * 0.30 / float(FACTORS["short_haul_flight"])
    events.append(make_event(prod, "PRE_PRODUCTION", "SCOPE_3", "TRANSPORT", "short_haul_flight",
                             round(short_haul_km, 1), "KM", FACTORS["short_haul_flight"],
                             "TIER_2", "travel_manifest_domestic", prod["primary_region"]))
    
    # Long-haul flights (international cast)
    long_haul_km = float(flight_kgco2e) * 0.70 / float(FACTORS["long_haul_flight"])
    events.append(make_event(prod, "PRE_PRODUCTION", "SCOPE_3", "TRANSPORT", "long_haul_flight",
                             round(long_haul_km, 1), "KM", FACTORS["long_haul_flight"],
                             "TIER_2", "travel_manifest_intl", prod["primary_region"]))
    
    # Ground transport (crew shuttles, vans)
    ground_kgco2e = float(travel_kgco2e) * 0.25
    coach_km = ground_kgco2e * 0.60 / float(FACTORS["coach"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "TRANSPORT", "coach",
                             round(coach_km, 1), "KM", FACTORS["coach"],
                             "TIER_2", "transport_contract", prod["primary_region"]))
    
    diesel_car_km = ground_kgco2e * 0.40 / float(FACTORS["medium_car_diesel"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "TRANSPORT", "medium_car_diesel",
                             round(diesel_car_km, 1), "KM", FACTORS["medium_car_diesel"],
                             "TIER_2", "vehicle_log", prod["primary_region"]))
    
    # --- ACCOMMODATION (Scope 3) ---
    accom_kgco2e = total_kg_f * splits["accommodation"]
    hotel_nights = float(accom_kgco2e) / float(FACTORS["hotel_night"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "ACCOMMODATION", "hotel",
                             round(hotel_nights, 1), "NIGHTS", FACTORS["hotel_night"],
                             "TIER_2", "hotel_booking_summary", prod["primary_region"]))
    
    # --- WASTE (Scope 3) ---
    waste_kgco2e = total_kg_f * 0.03  # ~3% of total for most productions
    landfill_kg = float(waste_kgco2e) * 0.40 / float(FACTORS["landfill_waste"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "WASTE", "landfill_general",
                             round(landfill_kg, 1), "KG", FACTORS["landfill_waste"],
                             "TIER_1", "waste_weighbridge_ticket", prod["primary_region"]))
    
    recycle_kg = float(waste_kgco2e) * 0.50 / float(FACTORS["recycling_mixed"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "WASTE", "recycling_mixed",
                             round(recycle_kg, 1), "KG", FACTORS["recycling_mixed"],
                             "TIER_1", "waste_diversion_cert", prod["primary_region"]))
    
    compost_kg = float(waste_kgco2e) * 0.10 / float(FACTORS["compost_waste"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "WASTE", "compost",
                             round(compost_kg, 1), "KG", FACTORS["compost_waste"],
                             "TIER_1", "compost_hauler_receipt", prod["primary_region"]))
    
    # --- MATERIALS (Scope 3) ---
    materials_kgco2e = total_kg_f * 0.04
    lumber_kg = float(materials_kgco2e) * 0.60 / float(FACTORS["lumber"])
    events.append(make_event(prod, "PRE_PRODUCTION", "SCOPE_3", "MATERIALS", "lumber_general",
                             round(lumber_kg, 1), "KG", FACTORS["lumber"],
                             "TIER_2", "set_construction_invoice", prod["primary_region"]))
    
    steel_kg = float(materials_kgco2e) * 0.40 / float(FACTORS["steel"])
    events.append(make_event(prod, "PRE_PRODUCTION", "SCOPE_3", "MATERIALS", "steel",
                             round(steel_kg, 1), "KG", FACTORS["steel"],
                             "TIER_2", "scaffolding_rental", prod["primary_region"]))
    
    # --- CATERING (Scope 3) ---
    catering_kgco2e = total_kg_f * 0.02
    beef_kg = float(catering_kgco2e) * 0.30 / float(FACTORS["beef"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "CATERING", "beef",
                             round(beef_kg, 2), "KG", FACTORS["beef"],
                             "TIER_2", "catering_inventory", prod["primary_region"]))
    
    chicken_kg = float(catering_kgco2e) * 0.40 / float(FACTORS["chicken"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "CATERING", "chicken",
                             round(chicken_kg, 2), "KG", FACTORS["chicken"],
                             "TIER_2", "catering_inventory", prod["primary_region"]))
    
    veg_kg = float(catering_kgco2e) * 0.30 / float(FACTORS["vegetables"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "CATERING", "vegetables",
                             round(veg_kg, 2), "KG", FACTORS["vegetables"],
                             "TIER_2", "catering_inventory", prod["primary_region"]))
    
    # --- WATER (Scope 3) ---
    water_kgco2e = total_kg_f * 0.005
    water_m3 = float(water_kgco2e) / float(FACTORS["water_supply"])
    events.append(make_event(prod, "PRODUCTION", "SCOPE_3", "WATER", "water_supply",
                             round(water_m3, 1), "M3", FACTORS["water_supply"],
                             "TIER_2", "water_utility_bill", prod["primary_region"]))
    
    # --- POST-PRODUCTION / VFX (Scope 3) ---
    if prod["vfx_intensity"] in ["HIGH", "EXTREME"]:
        vfx_kgco2e = total_kg_f * 0.05
        vfx_kwh = float(vfx_kgco2e) / float(grid_factor)
        events.append(make_event(prod, "POST_PRODUCTION", "SCOPE_3", "POST_VFX", "vfx_render_farm",
                                 round(vfx_kwh, 1), "KWH", grid_factor,
                                 "TIER_2", "render_farm_bill", prod["primary_region"]))
    
    return events


def make_event(prod, phase, scope, category, subcategory, value, unit, factor_value, 
               confidence_tier, source_ref, region):
    """Create a single activity event record."""
    kgco2e = Decimal(str(value)) * factor_value
    
    confidence_scores = {"TIER_1": Decimal("0.95"), "TIER_2": Decimal("0.75"), "TIER_3": Decimal("0.55")}
    
    # Add small noise to confidence
    base_conf = confidence_scores[confidence_tier]
    noise = Decimal(str(random.uniform(-0.03, 0.02)))
    confidence_score = max(Decimal("0.0"), min(Decimal("1.0"), base_conf + noise))
    
    return {
        "event_id": str(uuid.uuid4()),
        "production_id": prod["id"],
        "phase": phase,
        "scope": scope,
        "category": category,
        "subcategory": subcategory,
        "value": round(Decimal(str(value)), 4),
        "unit": unit,
        "kgco2e": round(kgco2e, 4),
        "confidence_tier": confidence_tier,
        "confidence_score": round(confidence_score, 2),
        "source_type": "MANUAL_ENTRY" if confidence_tier == "TIER_1" else "INVOICE_OCR",
        "source_reference": source_ref,
        "grid_region": region,
        "recorded_at": (datetime(2024, random.randint(1, 12), random.randint(1, 28)) 
                        + timedelta(days=random.randint(0, 30))).isoformat(),
    }


# ============================================================================
# EMISSION FACTORS SEED DATA
# ============================================================================

EMISSION_FACTORS = [
    # FUELS - Scope 1
    ("DEFRA", "ENERGY", "diesel_generator", "diesel_generator", "2.54600", "LITRES", "SCOPE_1", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "ENERGY", "petrol_vehicle", "petrol_vehicle", "2.13600", "LITRES", "SCOPE_1", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "ENERGY", "hvo_fuel", "hvo_fuel", "0.19500", "LITRES", "SCOPE_1", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "ENERGY", "natural_gas", "natural_gas", "0.18200", "KWH", "SCOPE_1", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "ENERGY", "lpg", "lpg", "1.49000", "LITRES", "SCOPE_1", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "ENERGY", "kerosene", "kerosene", "2.52000", "LITRES", "SCOPE_1", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    
    # ELECTRICITY - Scope 2
    ("DEFRA", "ENERGY", "grid_electricity", "grid_electricity_uk", "0.20700", "KWH", "SCOPE_2", "UK", "207.00", "2024-07-01", "DEFRA-2024-v1"),
    ("EPA", "ENERGY", "grid_electricity", "grid_electricity_us", "0.39000", "KWH", "SCOPE_2", "US", "390.00", "2024-06-01", "EPA-2024-v1"),
    ("BAFTA_ALBERT", "ENERGY", "grid_electricity", "grid_electricity_eu", "0.27800", "KWH", "SCOPE_2", "EU", "278.00", "2024-07-01", "ALBERT-2024-v1"),
    
    # TRANSPORT - Scope 3
    ("DEFRA", "TRANSPORT", "short_haul_flight", "short_haul_flight", "0.15800", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "long_haul_flight", "long_haul_flight", "0.19500", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "medium_car_petrol", "medium_car_petrol", "0.19200", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "medium_car_diesel", "medium_car_diesel", "0.17100", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "coach", "coach", "0.02700", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "local_bus", "local_bus", "0.10300", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "rail_national", "rail_national", "0.03600", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "taxi_black_cab", "taxi_black_cab", "0.16300", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "hgv_diesel", "hgv_diesel", "0.10600", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "TRANSPORT", "electric_car", "electric_car", "0.04700", "KM", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    
    # ACCOMMODATION - Scope 3
    ("DEFRA", "ACCOMMODATION", "hotel", "hotel_uk", "10.40000", "NIGHTS", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("EPA", "ACCOMMODATION", "hotel", "hotel_us", "15.20000", "NIGHTS", "SCOPE_3", "US", None, "2024-06-01", "EPA-2024-v1"),
    
    # WASTE - Scope 3
    ("DEFRA", "WASTE", "landfill_general", "landfill_general", "0.50000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "WASTE", "recycling_mixed", "recycling_mixed", "0.02000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "WASTE", "compost", "compost", "0.01000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "WASTE", "incineration", "incineration", "0.21000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    
    # WATER - Scope 3
    ("DEFRA", "WATER", "water_supply", "water_supply", "0.15000", "M3", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "WATER", "wastewater_treatment", "wastewater_treatment", "0.27000", "M3", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    
    # MATERIALS - Scope 3
    ("DEFRA", "MATERIALS", "lumber_general", "lumber_general", "0.50000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "steel", "steel", "1.35000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "aluminium", "aluminium", "6.70000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "plywood", "plywood", "0.82000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "paint", "paint", "2.90000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "paper", "paper", "0.94000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "cardboard", "cardboard", "0.41000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "glass", "glass", "1.10000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "plastic_pet", "plastic_pet", "2.55000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "fabric_cotton", "fabric_cotton", "8.30000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "MATERIALS", "foam_polyurethane", "foam_polyurethane", "3.40000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    
    # CATERING - Scope 3
    ("DEFRA", "CATERING", "beef", "beef", "60.00000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "lamb", "lamb", "24.00000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "chicken", "chicken", "6.10000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "pork", "pork", "7.20000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "fish", "fish", "3.90000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "dairy_milk", "dairy_milk", "1.30000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "eggs", "eggs", "2.10000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "vegetables", "vegetables", "0.50000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "rice", "rice", "3.70000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    ("DEFRA", "CATERING", "bread", "bread", "0.97000", "KG", "SCOPE_3", "UK", None, "2024-07-01", "DEFRA-2024-v1"),
    
    # POST-PRODUCTION / VFX - Scope 3
    ("DEFRA", "POST_VFX", "vfx_render_farm", "vfx_render_farm", "0.20700", "KWH", "SCOPE_3", "UK", "207.00", "2024-07-01", "DEFRA-2024-v1"),
    ("EPA", "POST_VFX", "vfx_render_farm", "vfx_render_farm_us", "0.39000", "KWH", "SCOPE_3", "US", "390.00", "2024-06-01", "EPA-2024-v1"),
    ("DEFRA", "POST_VFX", "edit_suite", "edit_suite", "0.20700", "KWH", "SCOPE_3", "UK", "207.00", "2024-07-01", "DEFRA-2024-v1"),
]


# ============================================================================
# DOCUMENT SAMPLES
# ============================================================================

DOCUMENTS = [
    {
        "doc_id": str(uuid.uuid4()),
        "production_id": PRODUCTIONS[0]["id"],  # The Midnight Heist
        "doc_type": "FUEL_RECEIPT",
        "filename": "diesel_delivery_march2024.pdf",
        "ocr_status": "EXTRACTED",
        "extracted_confidence": Decimal("0.91"),
        "extracted_by_model": "claude-haiku-4.5",
        "review_status": "APPROVED",
    },
    {
        "doc_id": str(uuid.uuid4()),
        "production_id": PRODUCTIONS[1]["id"],  # Crown & Dagger
        "doc_type": "ELECTRICITY_BILL",
        "filename": "pinewood_electricity_q2.pdf",
        "ocr_status": "EXTRACTED",
        "extracted_confidence": Decimal("0.88"),
        "extracted_by_model": "gpt-4o-mini",
        "review_status": "APPROVED",
    },
    {
        "doc_id": str(uuid.uuid4()),
        "production_id": PRODUCTIONS[2]["id"],  # Coastal Kitchen
        "doc_type": "TRAVEL_MANIFEST",
        "filename": "crew_flights_cornwall.xlsx",
        "ocr_status": "REVIEW_REQUIRED",
        "extracted_confidence": Decimal("0.62"),
        "extracted_by_model": "claude-haiku-4.5",
        "review_status": "PENDING",
    },
    {
        "doc_id": str(uuid.uuid4()),
        "production_id": PRODUCTIONS[3]["id"],  # The Last Colony
        "doc_type": "CATERING_INVOICE",
        "filename": "catering_week12_invoice.pdf",
        "ocr_status": "EXTRACTED",
        "extracted_confidence": Decimal("0.79"),
        "extracted_by_model": "gpt-4o-mini",
        "review_status": "APPROVED",
    },
    {
        "doc_id": str(uuid.uuid4()),
        "production_id": PRODUCTIONS[4]["id"],  # Laugh Track Live
        "doc_type": "WASTE_TICKET",
        "filename": "waste_diversion_cert_may.pdf",
        "ocr_status": "PENDING",
        "extracted_confidence": None,
        "extracted_by_model": None,
        "review_status": "PENDING",
    },
]


# ============================================================================
# CSV WRITERS
# ============================================================================

def write_productions():
    with open("sample_productions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "production_id", "title", "type", "genre", "budget_band", "runtime_min",
            "episodes", "shoot_days", "locations", "cast_count", "crew_count",
            "vfx_intensity", "status", "primary_region"
        ])
        for p in PRODUCTIONS:
            writer.writerow([
                p["id"], p["title"], p["type"], p["genre"], p["budget_band"],
                p["runtime_min"], p["episodes"], p["shoot_days"],
                "|".join(p["locations"]), p["cast_count"], p["crew_count"],
                p["vfx_intensity"], p["status"], p["primary_region"]
            ])


def write_events():
    all_events = []
    for prod in PRODUCTIONS:
        all_events.extend(generate_events_for_production(prod))
    
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
    return len(all_events)


def write_factors():
    with open("sample_emission_factors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "factor_id", "standard", "category", "subcategory", "activity_type",
            "factor_value", "unit", "scope", "region", "country_code",
            "grid_intensity_g_co2_kwh", "valid_from", "version"
        ])
        for i, row in enumerate(EMISSION_FACTORS):
            factor_id = str(uuid.uuid4())
            writer.writerow([
                factor_id, row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                row[7], row[7][:2] if row[7] != "Global" else None, row[8],
                row[9], row[10]
            ])


def write_documents():
    with open("sample_documents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "doc_id", "production_id", "doc_type", "filename", "ocr_status",
            "extracted_confidence", "extracted_by_model", "review_status"
        ])
        for d in DOCUMENTS:
            writer.writerow([
                d["doc_id"], d["production_id"], d["doc_type"], d["filename"],
                d["ocr_status"], d["extracted_confidence"], d["extracted_by_model"],
                d["review_status"]
            ])


def write_validation_report(event_count):
    """Generate a validation report showing totals per production."""
    print("=" * 70)
    print("SYNTHETIC TEST DATA GENERATION REPORT")
    print("=" * 70)
    print(f"\nTotal Productions: {len(PRODUCTIONS)}")
    print(f"Total Activity Events: {event_count}")
    print(f"Total Emission Factors: {len(EMISSION_FACTORS)}")
    print(f"Total Documents: {len(DOCUMENTS)}")
    
    print("\n" + "-" * 70)
    print("PRODUCTION SUMMARIES (Validate against benchmarks)")
    print("-" * 70)
    print(f"{'Title':<30} {'Type':<12} {'Benchmark':<12} {'Events':<8} {'Status'}")
    print("-" * 70)
    
    for p in PRODUCTIONS:
        base = BENCHMARKS.get((p["benchmark_type"], p["benchmark_size"]), 0)
        if p["type"] == "TV_SERIES":
            base *= p["episodes"]
        ev_count = sum(1 for e in all_events if e["production_id"] == p["id"])
        print(f"{p['title'][:29]:<30} {p['type']:<12} {base:>8.0f} tCO2e  {ev_count:<8} {p['status']}")
    
    print("\n" + "=" * 70)
    print("FILES CREATED:")
    print("  - sample_productions.csv")
    print("  - sample_activity_events.csv")
    print("  - sample_emission_factors.csv")
    print("  - sample_documents.csv")
    print("=" * 70)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    write_productions()
    write_factors()
    event_count = write_events()
    write_documents()
    
    # Reload events for report
    all_events = []
    for prod in PRODUCTIONS:
        all_events.extend(generate_events_for_production(prod))
    
    write_validation_report(len(all_events))
