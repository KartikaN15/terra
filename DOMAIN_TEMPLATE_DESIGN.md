# Domain-Agnostic Template Architecture

> The Netflix Production Sustainability Framework is **one instance** of a universal pattern.  
> This doc defines how to templatize the backend so it works for **any industry** without a rewrite.

---

## 1. The Universal Pattern

Every carbon-tracking domain follows the same 4-entity model:

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   PROJECT   │────▶│  ACTIVITY EVENT │────▶│  EMISSION FACTOR│────▶│  CALCULATION │
│  (anything) │     │  (what happened)│     │  (kgCO₂e/unit)  │     │  (result)    │
└─────────────┘     └─────────────────┘     └─────────────────┘     └──────────────┘
```

| Film/TV Term | Generic Term | Construction Example | Logistics Example |
|-------------|------------|---------------------|-------------------|
| Production | **Project** | Building Site A | Delivery Route #4421 |
| Genre | **Project Type** | Residential / Commercial | Last-mile / Long-haul |
| Budget Band | **Scale Band** | <$1M / $1-10M / >$10M | <100 stops / 100-500 / >500 |
| Shoot Days | **Duration** | Construction months | Route days |
| Cast/Crew | **Headcount** | Workers on site | Drivers + warehouse staff |
| VFX Intensity | **Complexity Score** | LEED certification level | Refrigerated / Hazardous |
| Episodes | **Output Units** | Floors completed | Pallets delivered |
| Runtime | **Output Size** | Square meters built | Ton-miles |

---

## 2. Templatization Strategy

### 2.1 Configurable Taxonomy (YAML/JSON)

Instead of hardcoding enums like `DRAMA`, `COMEDY`, `ACTION`, the system loads a **domain config** at startup:

```yaml
# domains/film_tv.yaml
domain_name: "film_tv"
display_name: "Film & Television Production"

project_types:
  - key: FEATURE
    display: "Feature Film"
    metadata_fields:
      - name: genre
        type: enum
        values: [ACTION, COMEDY, DRAMA, HORROR, SCI_FI, DOCUMENTARY]
      - name: budget_band
        type: enum
        values: [UNDER_1M, _1M_TO_5M, _5M_TO_10M, _10M_TO_50M, OVER_50M]
      - name: runtime_min
        type: integer
        unit: "minutes"
      - name: episodes
        type: integer
        default: 1
      - name: vfx_intensity
        type: enum
        values: [NONE, LOW, MEDIUM, HIGH, EXTREME]
      - name: shoot_days
        type: integer
        unit: "days"
      - name: locations
        type: string_list
      - name: cast_count
        type: integer
      - name: crew_count
        type: integer

activity_categories:
  - key: ENERGY
    display: "Energy & Fuel"
    scope_default: SCOPE_1
    subcategories:
      - diesel_generator
      - hvo_fuel
      - grid_electricity
      - natural_gas
  - key: TRANSPORT
    display: "Travel & Transport"
    scope_default: SCOPE_3
    subcategories:
      - short_haul_flight
      - long_haul_flight
      - medium_car_diesel
      - coach
  - key: MATERIALS
    display: "Materials"
    scope_default: SCOPE_3
    subcategories:
      - lumber_general
      - steel
      - paint
  - key: WASTE
    display: "Waste & Disposal"
    scope_default: SCOPE_3
    subcategories:
      - landfill_general
      - recycling_mixed
      - compost
  - key: CATERING
    display: "Catering"
    scope_default: SCOPE_3
    subcategories:
      - beef
      - chicken
      - vegetables
  - key: WATER
    display: "Water"
    scope_default: SCOPE_3
    subcategories:
      - water_supply
  - key: ACCOMMODATION
    display: "Accommodation"
    scope_default: SCOPE_3
    subcategories:
      - hotel
  - key: POST_VFX
    display: "Post-Production & VFX"
    scope_default: SCOPE_3
    subcategories:
      - vfx_render_farm
      - edit_suite

phases:
  - DEVELOPMENT
  - PRE_PRODUCTION
  - PRODUCTION
  - POST_PRODUCTION
  - DISTRIBUTION

intensity_metric:
  formula: "total_tco2e / (runtime_min / 60)"
  display: "tCO₂e per broadcast hour"
```

```yaml
# domains/construction.yaml
domain_name: "construction"
display_name: "Construction & Real Estate"

project_types:
  - key: BUILDING
    display: "Building Project"
    metadata_fields:
      - name: building_type
        type: enum
        values: [RESIDENTIAL, COMMERCIAL, INDUSTRIAL, INFRASTRUCTURE]
      - name: floor_area_m2
        type: decimal
        unit: "m²"
      - name: floors_above_ground
        type: integer
      - name: leed_level
        type: enum
        values: [NONE, CERTIFIED, SILVER, GOLD, PLATINUM]
      - name: construction_months
        type: integer
        unit: "months"
      - name: concrete_volume_m3
        type: decimal
        unit: "m³"
      - name: steel_tonnage
        type: decimal
        unit: "tonnes"
      - name: worker_headcount_avg
        type: integer

activity_categories:
  - key: MATERIALS
    display: "Construction Materials"
    subcategories:
      - concrete_ready_mix
      - steel_rebar
      - glass_facade
      - timber_structural
      - insulation
  - key: ENERGY
    display: "Site Energy"
    subcategories:
      - diesel_equipment
      - grid_electricity_site
      - natural_gas_heating
  - key: TRANSPORT
    display: "Material Transport"
    subcategories:
      - truck_delivery
      - rail_freight
  - key: WASTE
    display: "Construction Waste"
    subcategories:
      - concrete_demolition
      - mixed_waste_landfill
      - waste_recycling

intensity_metric:
  formula: "total_tco2e / floor_area_m2"
  display: "tCO₂e per m² built"
```

### 2.2 Dynamic Enum Loading

```python
# Instead of:
class Genre(Enum):
    DRAMA = "DRAMA"
    COMEDY = "COMEDY"

# The system does:
DomainRegistry = load_domain_config("domains/film_tv.yaml")
Genre = DomainRegistry.get_enum("genre")
# → dynamically created Enum at runtime
```

### 2.3 ML Feature Engineering is Domain-Agnostic

The ML models don't care that `vfx_intensity` means visual effects. They just see:

```
feature_vector = [
    project_type_encoded,      # categorical
    scale_band_encoded,        # categorical
    duration,                  # numeric
    headcount,                 # numeric
    complexity_score,          # categorical
    output_units,              # numeric
    output_size,               # numeric
]
```

The **feature engineering pipeline** maps domain-specific field names to generic feature names:

```python
FEATURE_MAP = {
    "film_tv": {
        "project_type": "genre",
        "scale_band": "budget_band",
        "duration": "shoot_days",
        "headcount": "crew_count",
        "complexity": "vfx_intensity",
        "output_units": "episodes",
        "output_size": "runtime_min",
    },
    "construction": {
        "project_type": "building_type",
        "scale_band": "floor_area_m2_binned",
        "duration": "construction_months",
        "headcount": "worker_headcount_avg",
        "complexity": "leed_level",
        "output_units": "floors_above_ground",
        "output_size": "floor_area_m2",
    }
}
```

### 2.4 Database Schema   — Same Tables, Dynamic Constraints

The PostgreSQL schema stays **identical** across domains. Only the **application-level validation** changes:

```sql
-- Same table for all domains
CREATE TABLE projects (
    project_id UUID PRIMARY KEY,
    domain VARCHAR(50) NOT NULL,  -- 'film_tv', 'construction', etc.
    project_type VARCHAR(50),     -- validated against domain config
    metadata JSONB NOT NULL,      -- flexible per-domain fields
    ...
);
```

### 2.5 Calculation Engine   — Already Universal

`ActivityEvent × EmissionFactor → kgCO₂e` works identically for:
- Diesel generator on a film set
- Diesel excavator on a construction site
- Diesel truck on a delivery route

Only the **factor lookup key** changes: `diesel_generator` → `diesel_equipment` → `diesel_truck`

---

## 3. Multi-Domain Deployment Modes

| Mode | Use Case | Implementation |
|------|----------|---------------|
| **Single-domain** | One company, one industry | Load one YAML config at startup |
| **Multi-tenant** | SaaS serving multiple industries | `domain` column on every table, config per tenant |
| **Hybrid** | Large org with multiple divisions | One instance, multiple active domain configs |

---

## 4. What This Means for the ML Engine

The ML code I'm building next is **already domain-agnostic**:

- `GreenlightPredictor` takes a generic feature vector → predicts total carbon
- `CategoryImputer` takes known categories + project metadata → imputes missing ones
- `AnomalyDetector` takes time-series of kgCO₂e → flags outliers

The only domain-specific piece is the **feature extractor** that maps project metadata → feature vector. That lives in a pluggable config, not in the model code.

---

## 5. Summary: From Framework to Template

| Layer | Film/TV Specific | Generic Template |
|-------|-----------------|------------------|
| Database Schema | Hardcoded enums | `domain` column + JSONB metadata |
| API Validation | Pydantic with film fields | Pydantic with dynamic fields from YAML |
| Calculation Engine | Film-specific factor keys | Configurable category/subcategory taxonomy |
| ML Features | `vfx_intensity`, `shoot_days` | Generic: `complexity`, `duration`, `headcount` |
| Reporting | `tCO₂e/hour of broadcast` | Configurable `intensity_metric.formula` |
| UI Labels | "Production", "Episodes" | Loaded from domain config `display_name` |

**The ML logic is the universal kernel. The domain config is the interchangeable shell.**
