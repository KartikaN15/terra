# Datasets & Test Data Strategy

> Research-backed collection of real benchmarks, open datasets, and synthetic data generators for testing the Production Sustainability backend.

---

## 1. Real Industry Benchmarks (Hard Data)

### A. SPA / Green Production Alliance Report (2021)
**Source:** `greenproductionguide.com`   — PEAR calculator data from 159+ TV productions and feature films.

| Production Type | Avg Footprint | Per-Episode / Per-Day |
|----------------|---------------|----------------------|
| **Tentpole Film** ($70M+) | 3,370 tCO₂e | ~33 tCO₂e/shoot day |
| **Large Film** ($40-70M) | 1,081 tCO₂e |   \|
| **Medium Film** ($20-40M) | 769 tCO₂e |   \|
| **Small Film** (<$20M) | 391 tCO₂e |   \|
| **1-Hour Scripted Drama** | 77 tCO₂e/episode |   \|
| **½-Hour Single-Cam** | 26 tCO₂e/episode |   \|
| **½-Hour Multi-Cam** | 18 tCO₂e/episode |   \|
| **Unscripted TV** | 13 tCO₂e/episode |   \|

**Category Breakdown (Tentpole):**
- Fuel (vehicles + generators): **48%**
- Air Travel: **24%**
- Utilities (electricity/gas): **22%**
- Accommodation: **6%**

**Category Breakdown (1-Hour Drama):**
- Fuel: largest contributor
- Utilities: largest for multi-cam (49%)
- Air Travel: largest for unscripted (61%)

### B. BAFTA albert Industry Data (2024)
**Source:** `wearealbert.org`   \2,500+ UK productions

- Total UK production industry: **175,000 tCO₂e** (2024)
- Average: **16.6 tCO₂e per hour of content** (2023)
- 3,000 footprints processed in 2023
- 467 international productions across 38 countries

### C. Netflix Public ESG Data
**Source:** Netflix ESG Reports (public PDFs)

| Year | Scope 1 | Scope 2 (Loc) | Scope 3 | Total |
|------|---------|---------------|---------|-------|
| 2019 | 51,487 | 26,594 | 1,192,659 | 1,270,740 |
| 2020 | 30,883 | 28,585 | 1,020,541 | 1,080,009 |
| 2021 | 62,815 | 42,291 | 1,466,497 | 1,571,603 |
| 2022 | 59,388 | 41,411 | 1,086,833 | 1,211,788 |
| 2023 | 25,790 | 30,303 | 840,778 | 896,871 |
| 2024 | 50,488 | 40,684 | 1,037,226 | 1,129,124 |

**Netflix Breakdown (2024):**
- Corporate (offices, travel, cloud): **61%**
- Production (film/series/games): **35%**
- Streaming (CDN, data centers): **5%**

---

## 2. Open Emission Factor Datasets (Downloadable)

### A. DEFRA UK Government Conversion Factors ⭐ PRIMARY
**URL:** https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting

- **Format:** Excel workbook (.xlsx) with multiple tabs
- **Update:** Annual (July each year)
- **Coverage:**
  - Fuels (diesel, petrol, natural gas, LPG, kerosene, HVO, biodiesel)
  - Electricity (UK grid average, + country-specific factors via albert)
  - Transport (road, rail, air, sea)
  - Waste (landfill, recycling, compost, incineration)
  - Water (supply + treatment)
  - Materials (paper, timber, metals, plastics, glass, textiles)
  - Food & drink (beef, lamb, poultry, fish, dairy, vegetables)
  - Accommodation (hotel nights)
  - Refrigerants & F-gases

**Key Factors for Film/TV (DEFRA 2024):**
| Activity | Factor | Unit |
|----------|--------|------|
| Diesel (average bio blend) | 2.546 | kgCO₂e/L |
| Petrol (average bio blend) | 2.136 | kgCO₂e/L |
| HVO100 | 0.195 | kgCO₂e/L |
| Natural gas | 0.182 | kgCO₂e/kWh |
| UK Grid Electricity | 0.207 | kgCO₂e/kWh |
| Short-haul flight | 0.158 | kgCO₂e/km |
| Long-haul flight | 0.195 | kgCO₂e/km |
| Hotel (UK average) | 10.4 | kgCO₂e/room/night |
| Landfill (mixed waste) | 0.500 | kgCO₂e/kg |
| Recycling (mixed) | 0.020 | kgCO₂e/kg |

### B. EPA Emission Factors Hub (US)
**URL:** https://www.epa.gov/climateleadership/ghg-emission-factors-hub

- **Format:** Excel / PDF
- **Update:** Annual (September)
- **Coverage:** US-specific energy, transport, waste factors
- Good for US-based productions

### C. eGRID (US Electricity Grid)
**URL:** https://www.epa.gov/egrid

- Sub-region electricity grid intensity data
- Use for location-based Scope 2 calculations in the US

### D. Electricity Maps API
**URL:** https://app.electricitymaps.com/

- Real-time and historical grid carbon intensity by country/region
- API available for automated lookup
- Free tier: 1,000 requests/month

### E. Kaggle - CO2 Emission by Vehicles
**URL:** https://www.kaggle.com/datasets/debajiyitpoddder/co2-e-mission-by-vehicles

- Canadian government vehicle emission data
- Make, model, engine size, fuel consumption, CO₂ rating
- Useful for fleet/transport modeling

---

## 3. Synthetic Test Data Generator

Since **real production-level carbon data is proprietary** (BAFTA albert and Netflix don't release per-production CSVs), we generate realistic synthetic data using the known benchmarks above.

### Generator Logic
```python
# Pseudo-code for synthetic data generator

def generate_production(type, budget_band, genre, shoot_days, episodes=1):
    """Generate a realistic production with carbon events."""
    
    # Base footprint from SPA benchmarks with ±20% noise
    base_tco2e = lookup_benchmark(type, budget_band) * random(0.8, 1.2)
    
    # Distribute across categories using known breakdowns
    if type == FEATURE:
        fuel_pct = 0.48
        travel_pct = 0.24
        energy_pct = 0.22
        accom_pct = 0.06
    elif type == TV_SERIES and genre == DRAMA:
        fuel_pct = 0.35
        travel_pct = 0.30
        energy_pct = 0.25
        accom_pct = 0.10
    
    # Generate events for each category
    events = []
    events += generate_fuel_events(base_tco2e * fuel_pct, shoot_days)
    events += generate_travel_events(base_tco2e * travel_pct, shoot_days)
    events += generate_energy_events(base_tco2e * energy_pct, shoot_days)
    events += generate_accommodation_events(base_tco2e * accom_pct, shoot_days)
    
    return production, events
```

---

## 4. Sample Test CSV Files (Ready to Use)

I've created 4 sample files in `/test_data/`:

### `sample_productions.csv` (8 productions)
| id | title | type | genre | budget_band | shoot_days | episodes | vfx_intensity | status |
|----|-------|------|-------|-------------|------------|----------|---------------|--------|
| 1 | The Midnight Heist | FEATURE | ACTION | _10M_TO_50M | 45 | 1 | HIGH | PRODUCTION |
| 2 | Crown & Dagger S3 | TV_SERIES | DRAMA | _5M_TO_10M | 120 | 8 | MEDIUM | POST_PRODUCTION |
| 3 | Coastal Kitchen | TV_SERIES | REALITY | UNDER_1M | 30 | 12 | NONE | WRAPPED |

### `sample_activity_events.csv` (~200 events)
Realistic events across all scopes and categories:
- Diesel generator fuel logs (Scope 1)
- Grid electricity bills (Scope 2)
- Flight manifests (Scope 3)
- Hotel bookings (Scope 3)
- Waste weighbridge tickets (Scope 3)
- Catering invoices (Scope 3)

### `sample_emission_factors.csv` (50 core factors)
Seed data for your emission_factor table   — DEFRA 2024 values for the most common production activities.

### `sample_documents.csv` (5 documents)
Mock document records with extraction status for testing the OCR pipeline.

---

## 5. How to Use These for Testing

### Test 1: Calculation Accuracy
```python
# Load sample events + factors → run calculation engine
# Assert: total ≈ expected benchmark (within ±10%)
```

### Test 2: Scope Classification
```python
# Load all events → auto-classify scope
# Assert: diesel_generator → SCOPE_1, grid_electricity → SCOPE_2, flight → SCOPE_3
```

### Test 3: Aggregation
```python
# Load events for production_id=1 → run aggregator
# Assert: category_breakdown sums to total, confidence is weighted average
```

### Test 4: Bulk Import
```python
# POST sample_activity_events.csv → /api/v1/events/bulk
# Assert: 200 OK, row-level success/failure report, correct event count
```

### Test 5: Greenlight Prediction
```python
# Train model on 6 productions → predict production_id=7
# Assert: predicted_tco2e within ±30% of actual
```

---

## 6. Download Instructions

### Immediate (No API Key Needed)
1. **DEFRA Factors:** Go to https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting → Download "Condensed set (CSV format)"
2. **EPA Factors:** Go to https://www.epa.gov/climateleadership/ghg-emission-factors-hub → Download "GHG Emission Factors Hub (XLSX)"

### Requires API Key
3. **Electricity Maps:** Sign up at https://api-portal.electricitymaps.com/ → Free tier: 1,000 calls/month

### Already Created for You
4. **Synthetic production + event data:** See `/test_data/` folder in this repo

---

## 7. Data Quality Notes

| Issue | Mitigation |
|-------|------------|
| Synthetic data isn't real | Use real benchmarks as guardrails; validate totals against SPA/BAFTA averages |
| DEFRA factors are UK-only | Add EPA factors for US productions; flag "Global" fallback |
| Missing grid intensity for locations | Default to country average; flag confidence reduction |
| No historical time-series | Netflix ESG reports give year-over-year aggregates; use for trend validation |

---

*This gives you both real benchmarks to validate against AND ready-to-ingest test data for development.*
