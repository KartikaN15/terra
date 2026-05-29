"""
OED Playbook   — Optimise · Electrify · Decarbonise
Rule-based recommendation engine that suggests actions based on production data.
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Recommendation:
    id: str
    category: str
    action: str
    description: str
    estimated_saving_tco2e: Decimal
    estimated_cost_gbp: Optional[Decimal]
    effort: str  # LOW, MEDIUM, HIGH
    impact: str  # LOW, MEDIUM, HIGH
    playbook: str  # OPTIMISE, ELECTRIFY, DECARBONISE


# Simplified emission factors for impact estimation (tCO2e per unit action)
IMPACT_FACTORS = {
    "hvo_vs_diesel": Decimal("0.90"),  # ~90% reduction per litre switched
    "renewable_energy": Decimal("0.50"),  # ~50% grid reduction
    "green_hotel": Decimal("0.30"),  # ~30% hotel reduction
    "recycling_boost": Decimal("0.40"),  # ~40% waste reduction
    "plant_based_catering": Decimal("0.35"),  # ~35% catering reduction
    "travel_consolidation": Decimal("0.25"),  # ~25% travel reduction
    "virtual_production": Decimal("0.15"),  # ~15% total reduction
    "led_volume": Decimal("0.20"),  # ~20% set energy reduction
}


def generate_recommendations(
    category_breakdown: Dict[str, Decimal],
    total_tco2e: Decimal,
    production_meta: Optional[Dict[str, Any]] = None,
) -> List[Recommendation]:
    """
    Generate OED recommendations from a production's category breakdown.
    """
    recs: List[Recommendation] = []

    energy = category_breakdown.get("ENERGY", Decimal("0"))
    transport = category_breakdown.get("TRANSPORT", Decimal("0"))
    accommodation = category_breakdown.get("ACCOMMODATION", Decimal("0"))
    waste = category_breakdown.get("WASTE", Decimal("0"))
    catering = category_breakdown.get("CATERING", Decimal("0"))
    materials = category_breakdown.get("MATERIALS", Decimal("0"))

    # --- OPTIMISE ---
    if energy > total_tco2e * Decimal("0.20"):
        saving = energy * IMPACT_FACTORS["hvo_vs_diesel"] * Decimal("0.30")
        recs.append(Recommendation(
            id="opt-001",
            category="ENERGY",
            action="Switch 30% of diesel to HVO",
            description="HVO (hydrotreated vegetable oil) cuts generator emissions by ~90% with no equipment changes.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("2500"),
            effort="LOW",
            impact="HIGH",
            playbook="OPTIMISE",
        ))

    if transport > total_tco2e * Decimal("0.20"):
        saving = transport * IMPACT_FACTORS["travel_consolidation"]
        recs.append(Recommendation(
            id="opt-002",
            category="TRANSPORT",
            action="Consolidate location travel",
            description="Reduce inter-city crew shuttles and batch travel days to cut total km by 25%.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("0"),
            effort="LOW",
            impact="MEDIUM",
            playbook="OPTIMISE",
        ))

    if waste > total_tco2e * Decimal("0.05"):
        saving = waste * IMPACT_FACTORS["recycling_boost"]
        recs.append(Recommendation(
            id="opt-003",
            category="WASTE",
            action="Boost recycling rate to 80%",
            description="Add on-set colour-coded bins and a dedicated waste coordinator.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("800"),
            effort="LOW",
            impact="MEDIUM",
            playbook="OPTIMISE",
        ))

    # --- ELECTRIFY ---
    if energy > total_tco2e * Decimal("0.15"):
        saving = energy * IMPACT_FACTORS["renewable_energy"]
        recs.append(Recommendation(
            id="ele-001",
            category="ENERGY",
            action="Purchase renewable grid energy",
            description="Switch studio and basecamp electricity to 100% renewable tariff.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("1200"),
            effort="LOW",
            impact="HIGH",
            playbook="ELECTRIFY",
        ))

    if production_meta and production_meta.get("vfx_intensity") in ["HIGH", "EXTREME"]:
        saving = total_tco2e * Decimal("0.03")
        recs.append(Recommendation(
            id="ele-002",
            category="POST_VFX",
            action="Move render farm to cloud region with renewables",
            description="AWS/GCP regions like eu-north-1 run on 90%+ renewable energy.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("500"),
            effort="MEDIUM",
            impact="MEDIUM",
            playbook="ELECTRIFY",
        ))

    # --- DECARBONISE ---
    if accommodation > total_tco2e * Decimal("0.05"):
        saving = accommodation * IMPACT_FACTORS["green_hotel"]
        recs.append(Recommendation(
            id="dec-001",
            category="ACCOMMODATION",
            action="Block-book green-certified hotels",
            description="Choose Green Key or EarthCheck certified properties for the crew block.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("0"),
            effort="LOW",
            impact="MEDIUM",
            playbook="DECARBONISE",
        ))

    if catering > total_tco2e * Decimal("0.05"):
        saving = catering * IMPACT_FACTORS["plant_based_catering"]
        recs.append(Recommendation(
            id="dec-002",
            category="CATERING",
            action="Default to plant-based catering 2 days/week",
            description="Beef has ~10× the footprint of plant proteins. Two meat-free days cuts catering emissions significantly.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("-400"),
            effort="LOW",
            impact="HIGH",
            playbook="DECARBONISE",
        ))

    if materials > total_tco2e * Decimal("0.05"):
        saving = materials * Decimal("0.25")
        recs.append(Recommendation(
            id="dec-003",
            category="MATERIALS",
            action="Rent vs buy set construction",
            description="Rent modular sets and reuse lumber across productions to cut embodied carbon.",
            estimated_saving_tco2e=round(saving, 2),
            estimated_cost_gbp=Decimal("-1500"),
            effort="MEDIUM",
            impact="MEDIUM",
            playbook="DECARBONISE",
        ))

    # Sort by estimated saving desc
    recs.sort(key=lambda r: r.estimated_saving_tco2e, reverse=True)
    return recs
