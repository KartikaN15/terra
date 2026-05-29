# Backend Logic Plan   — Production Sustainability Intelligence Platform

> **Research-backed by:** GHG Protocol Corporate Standard, BAFTA albert Calculator Methodology (Nov 2023), EPA/DEFRA emission factor databases, and production carbon tracking systems.

---

## 1. Core Calculation Formula (The Golden Rule)

Every emission calculation in the system follows the **GHG Protocol activity-based method**:

```
CO₂e (kg) = Activity Data × Emission Factor × Grid Intensity Modifier (if applicable)
```

Where:
- **Activity Data**: The measurable quantity (litres, kWh, km, kg, hours, spend £/$)
- **Emission Factor**: kgCO₂e per unit of activity (from DEFRA, EPA, IPCC, or custom EPDs)
- **Grid Intensity Modifier**: For electricity, converts generic kWh → location-specific kgCO₂e using gCO₂/kWh

**BAFTA albert adds:**
- Radiative forcing multiplier of **1.7×** for air travel (DEFRA advisory)
- Well-to-tank (WTT) factors for fuels (production/delivery emissions)
- Transmission & distribution (T&D) adders for certified renewable energy

---

## 2. Domain Models (The Backend Entities)

### 2.1 Production (The Root Aggregate)

```python
class Production:
    production_id: UUID
    title: str
    type: Enum[FEATURE, TV_SERIES, DOCUMENTARY, COMMERCIAL]
    genre: Enum[DRAMA, COMEDY, ACTION, HORROR, REALITY, ANIMATION, ...]
    budget_band: Enum[UNDER_1M, _1M_TO_5M, _5M_TO_10M, _10M_TO_50M, OVER_50M]
    runtime_min: int
    episodes: int = 1
    shoot_days: int
    locations: List[Location]
    cast_count: int
    crew_count: int
    vfx_intensity: Enum[NONE, LOW, MEDIUM, HIGH, EXTREME]
    status: Enum[DEVELOPMENT, PRE_PRODUCTION, PRODUCTION, POST_PRODUCTION, DISTRIBUTION, WRAPPED]
    
    # Carbon targets
    carbon_budget_tco2e: Decimal | None
    carbon_budget_source: Enum[GREENLIGHT_PREDICTION, MANUAL, BENCHMARK]
    
    # Tracking
    created_at: datetime
    updated_at: datetime
    created_by: UUID
```

### 2.2 ActivityEvent (The Core Fact Table)

This is the **most important table** in the system. Every litre of fuel, every kWh, every km traveled becomes one row.

```python
class ActivityEvent:
    event_id: UUID
    production_id: UUID  # FK → Production
    
    # Classification
    phase: Enum[DEVELOPMENT, PRE_PRODUCTION, PRODUCTION, POST_PRODUCTION, DISTRIBUTION]
    scope: Enum[SCOPE_1, SCOPE_2, SCOPE_3]
    category: Enum[ENERGY, TRANSPORT, ACCOMMODATION, MATERIALS, WASTE, WATER, CATERING, POST_VFX, CLOUD]
    subcategory: str  # e.g., "diesel_generator", "short_haul_flight", "studio_electricity"
    
    # Activity data (what was measured)
    value: Decimal
    unit: Enum[LITRES, KWH, KM, MILES, KG, HOURS, GBP, USD, TONNES, M3]
    
    # Calculation result (computed, not stored raw)
    kgco2e: Decimal
    kgco2e_wtt: Decimal | None  # Well-to-tank (optional)
    
    # Confidence & source
    confidence_tier: Enum[TIER_1_DIRECT, TIER_2_BENCHMARK, TIER_3_ML_IMPUTED]
    confidence_score: Decimal  # 0.0 - 1.0
    source_type: Enum[MANUAL_ENTRY, CSV_UPLOAD, IOT_STREAM, INVOICE_OCR, API_INTEGRATION, BENCHMARK]
    source_reference: str | None  # Invoice #, meter ID, filename, etc.
    
    # Emission factor used
    emission_factor_id: UUID  # FK → EmissionFactor
    emission_factor_version: str  # Version at time of calculation (immutable)
    
    # Location context
    location_id: UUID | None
    grid_region: str | None  # e.g., "UK", "California", "Germany"
    
    # Metadata
    recorded_by: UUID
    recorded_at: datetime
    notes: str | None
    
    # Audit trail (immutable after creation)
    calculated_at: datetime
    calculation_method: str
```

### 2.3 EmissionFactor (The Lookup Bible)

```python
class EmissionFactor:
    factor_id: UUID
    
    # Taxonomy
    standard: Enum[DEFRA, EPA, GHG_PROTOCOL, IPCC, BAFTA_ALBERT, CUSTOM_EPD]
    category: Enum[ENERGY, TRANSPORT, ACCOMMODATION, MATERIALS, WASTE, WATER, CATERING, POST_VFX]
    subcategory: str
    activity_type: str  # e.g., "diesel_generator", "commercial_air_travel_short_haul"
    
    # Factor value
    factor_value: Decimal  # e.g., 2.68
    unit: Enum[KG_CO2E_PER_LITRE, KG_CO2E_PER_KWH, KG_CO2E_PER_KM, KG_CO2E_PER_KG, KG_CO2E_PER_GBP]
    
    # Scope classification
    scope: Enum[SCOPE_1, SCOPE_2, SCOPE_3]
    
    # Geography
    region: str  # "UK", "US", "EU", "Global"
    country_code: str | None  # ISO 3166-1 alpha-2
    grid_intensity_g_co2_kwh: Decimal | None  # For electricity factors
    
    # Validity
    valid_from: date
    valid_to: date | None
    version: str  # e.g., "DEFRA-2023-v1"
    
    # Metadata
    source_url: str | None
    description: str
    is_active: bool
    
    # Special modifiers
    radiative_forcing_multiplier: Decimal = 1.0  # 1.7 for air travel
    wtt_factor: Decimal | None  # Well-to-tank addition
```

### 2.4 ProductionLocation

```python
class ProductionLocation:
    location_id: UUID
    production_id: UUID
    name: str  # "Pinewood Studio", "Location: Paris"
    location_type: Enum[STUDIO, ON_LOCATION, POST_FACILITY, OFFICE]
    address: str | None
    country_code: str
    region: str
    grid_intensity_g_co2_kwh: Decimal | None  # Fetched from Electricity Maps / cached
    
    # For studio benchmarks
    floor_area_m2: Decimal | None
    has_led_volume: bool = False
```

### 2.5 Document (Unstructured Data Pipeline)

```python
class Document:
    doc_id: UUID
    production_id: UUID
    doc_type: Enum[FUEL_RECEIPT, ELECTRICITY_BILL, TRAVEL_MANIFEST, CATERING_INVOICE, WASTE_TICKET, EPD, OTHER]
    s3_path: str
    filename: str
    file_size_bytes: int
    mime_type: str
    
    # OCR / Extraction
    ocr_status: Enum[PENDING, PROCESSING, EXTRACTED, REVIEW_REQUIRED, APPROVED, REJECTED]
    extracted_raw_text: str | None
    extracted_data: JSON  # Structured JSON from LLM
    extracted_confidence: Decimal | None
    extracted_by_model: str | None  # "claude-haiku-4.5", "gpt-4o"
    
    # Human review
    review_status: Enum[PENDING, APPROVED, REJECTED, CORRECTED]
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    review_notes: str | None
    
    # Linked events (once approved, creates ActivityEvents)
    linked_event_ids: List[UUID]
    
    uploaded_at: datetime
    uploaded_by: UUID
```

### 2.6 CarbonForecast (ML Predictions)

```python
class CarbonForecast:
    forecast_id: UUID
    production_id: UUID
    model_version: str
    model_type: Enum[GREENLIGHT_PREDICTOR, CATEGORY_IMPUTER, ANOMALY_DETECTOR]
    
    # Prediction
    predicted_tco2e: Decimal
    interval_lower: Decimal
    interval_upper: Decimal
    confidence: Decimal
    
    # Explainability (SHAP)
    feature_importance: JSON  # {"shoot_days": 0.32, "vfx_intensity": 0.28, ...}
    
    # Actual vs predicted (filled later)
    actual_tco2e: Decimal | None
    residual: Decimal | None
    
    created_at: datetime
```

### 2.7 Vendor (Supplier Scorecarding)

```python
class Vendor:
    vendor_id: UUID
    name: str
    category: Enum[POWER_RENTAL, TRANSPORT, CATERING, WASTE_HAULING, STUDIO, POST_FACILITY, EQUIPMENT]
    location: str
    green_certified: bool = False
    certification_type: str | None  # "Green Production Guide", "Albert Affiliate"
    
    # Emission performance
    avg_emission_factor: Decimal | None
    renewable_energy_share: Decimal | None  # 0.0 - 1.0
    
    # Scorecard
    productions_used_count: int
    total_spend_gbp: Decimal
    total_kgco2e: Decimal
    scorecard_rating: Enum[A_PLUS, A, B, C, D, UNRATED]
    
    # EPD / docs
    epd_document_id: UUID | None
    esg_report_url: str | None
```

---

## 3. Calculation Engine Logic

### 3.1 The Universal Calculation Service

```python
class CalculationEngine:
    """
    Core engine that converts ActivityEvent + EmissionFactor → kgCO2e.
    Stateless, deterministic, and fully auditable.
    """
    
    def calculate(self, event: ActivityEvent, factor: EmissionFactor) -> CalculationResult:
        """
        Primary calculation method.
        Formula: activity_value × emission_factor × modifiers
        """
        
        # Step 1: Unit conversion (normalize to factor's unit)
        normalized_value = self.unit_converter.convert(
            from_unit=event.unit,
            to_unit=factor.unit,
            value=event.value,
            context=event  # Some conversions need context (e.g., fuel density)
        )
        
        # Step 2: Base emissions
        base_kgco2e = normalized_value * factor.factor_value
        
        # Step 3: Apply location-based grid intensity for electricity
        if factor.category == ENERGY and factor.unit == KG_CO2E_PER_KWH:
            if event.grid_region and factor.grid_intensity_g_co2_kwh:
                # Override with location-specific intensity if available
                grid_modifier = self.get_grid_intensity(event.grid_region) / factor.grid_intensity_g_co2_kwh
                base_kgco2e = normalized_value * self.get_grid_intensity(event.grid_region) / 1000
        
        # Step 4: Apply radiative forcing for aviation
        if factor.category == TRANSPORT and "air" in factor.subcategory:
            base_kgco2e *= factor.radiative_forcing_multiplier  # 1.7 for air travel
        
        # Step 5: Add well-to-tank if applicable
        wtt_kgco2e = None
        if factor.wtt_factor:
            wtt_kgco2e = normalized_value * factor.wtt_factor
        
        # Step 6: Determine confidence tier
        confidence_tier = self.determine_confidence_tier(event, factor)
        confidence_score = self.compute_confidence_score(event, factor, confidence_tier)
        
        return CalculationResult(
            kgco2e=round(base_kgco2e, 4),
            kgco2e_wtt=round(wtt_kgco2e, 4) if wtt_kgco2e else None,
            confidence_tier=confidence_tier,
            confidence_score=confidence_score,
            emission_factor_id=factor.factor_id,
            emission_factor_version=factor.version,
            calculation_method=f"activity_based_{factor.standard.value}",
            calculated_at=datetime.utcnow()
        )
```

### 3.2 Confidence Scoring Logic (Tiered Model)

Directly implements the framework's **Tiered Confidence Model**:

```python
class ConfidenceScorer:
    """
    Assigns confidence tier and score based on data quality.
    """
    
    def determine_tier(self, event: ActivityEvent, factor: EmissionFactor) -> ConfidenceTier:
        """
        TIER 1   — Direct Measurement (Highest Confidence)
        Source: Meter readings, weighed receipts, IoT sensors, sub-metered data
        """
        if event.source_type in [IOT_STREAM, MANUAL_ENTRY] and event.source_reference:
            if self.is_meter_reading(event) or self.is_weighed_receipt(event):
                return TIER_1_DIRECT
        
        """
        TIER 2   — Benchmark / Spend-Based (Medium Confidence)
        Source: Invoices with spend data, benchmark estimates, vendor averages
        """
        if event.source_type in [INVOICE_OCR, CSV_UPLOAD, API_INTEGRATION]:
            if event.unit in [GBP, USD]:  # Spend-based
                return TIER_2_BENCHMARK
            if factor.subcategory.endswith("_benchmark"):
                return TIER_2_BENCHMARK
        
        """
        TIER 3   — ML Imputed / Statistical (Lower Confidence)
        Source: Predicted from production metadata, statistical extrapolation
        """
        if event.source_type == BENCHMARK or event.notes and "imputed" in event.notes.lower():
            return TIER_3_ML_IMPUTED
        
        # Default fallback
        return TIER_2_BENCHMARK
    
    def compute_score(self, tier: ConfidenceTier, event: ActivityEvent, factor: EmissionFactor) -> Decimal:
        """
        Base scores:
        - Tier 1: 0.90 - 0.99 (±5% error band)
        - Tier 2: 0.65 - 0.89 (±15-25% error band)
        - Tier 3: 0.40 - 0.64 (±30-50% error band)
        
        Adjusted by:
        - Factor age (older = lower)
        - Region specificity (global factor vs country-specific)
        - Data completeness
        """
        base_scores = {
            TIER_1_DIRECT: Decimal("0.95"),
            TIER_2_BENCHMARK: Decimal("0.78"),
            TIER_3_ML_IMPUTED: Decimal("0.55")
        }
        
        score = base_scores[tier]
        
        # Penalty: old emission factor (>2 years)
        factor_age_years = (date.today() - factor.valid_from).days / 365
        if factor_age_years > 2:
            score -= Decimal("0.05")
        
        # Penalty: global factor vs specific
        if factor.region == "Global" and factor.country_code is None:
            score -= Decimal("0.03")
        
        # Penalty: missing source reference
        if not event.source_reference:
            score -= Decimal("0.02")
        
        return max(Decimal("0.0"), min(Decimal("1.0"), score))
```

### 3.3 Scope Auto-Classification Rules

```python
class ScopeClassifier:
    """
    Automatically classifies activities into Scope 1, 2, or 3.
    Based on GHG Protocol Corporate Standard.
    """
    
    RULES = {
        # SCOPE 1   — Direct emissions (owned/controlled sources)
        SCOPE_1: [
            "diesel_generator",
            "natural_gas_heating",
            "propane_combustion",
            "company_vehicle_petrol",
            "company_vehicle_diesel",
            "hvo_fuel",
            "refrigerant_leakage",
        ],
        
        # SCOPE 2   — Indirect emissions from purchased energy
        SCOPE_2: [
            "grid_electricity",
            "purchased_heat",
            "purchased_steam",
            "purchased_cooling",
        ],
        
        # SCOPE 3   — Value chain emissions
        SCOPE_3: [
            "commercial_air_travel",
            "hotel_accommodation",
            "waste_landfill",
            "waste_recycling",
            "catering_services",
            "cloud_compute",
            "vfx_rendering",
            "freight_shipping",
            "employee_commuting",
            "purchased_materials",
        ]
    }
    
    def classify(self, subcategory: str) -> Scope:
        for scope, patterns in self.RULES.items():
            if any(pattern in subcategory for pattern in patterns):
                return scope
        
        # Default heuristic
        if "electricity" in subcategory and "generator" not in subcategory:
            return SCOPE_2
        if any(fuel in subcategory for fuel in ["diesel", "petrol", "gas", "propane", "hvo"]):
            return SCOPE_1
        
        return SCOPE_3  # Conservative default
```

---

## 4. Aggregation & Rollup Logic

### 4.1 Production-Level Aggregations

```python
class ProductionAggregator:
    """
    Computes all summary metrics for a production.
    """
    
    def aggregate(self, production_id: UUID) -> ProductionSummary:
        events = self.repo.get_events(production_id)
        
        # By Scope
        scope_totals = {
            SCOPE_1: sum(e.kgco2e for e in events if e.scope == SCOPE_1),
            SCOPE_2: sum(e.kgco2e for e in events if e.scope == SCOPE_2),
            SCOPE_3: sum(e.kgco2e for e in events if e.scope == SCOPE_3),
        }
        total_kgco2e = sum(scope_totals.values())
        
        # By Category (department view)
        category_totals = {}
        for cat in Category:
            category_totals[cat] = sum(e.kgco2e for e in events if e.category == cat)
        
        # By Phase (timeline view)
        phase_totals = {}
        for phase in Phase:
            phase_totals[phase] = sum(e.kgco2e for e in events if e.phase == phase)
        
        # Confidence-weighted score
        weighted_confidence = sum(
            e.kgco2e * e.confidence_score for e in events
        ) / total_kgco2e if total_kgco2e > 0 else Decimal("0")
        
        # Variance from budget
        budget_variance = None
        budget = self.repo.get_budget(production_id)
        if budget:
            budget_variance = (total_kgco2e / 1000 - budget.carbon_budget_tco2e) / budget.carbon_budget_tco2e
        
        # Intensity metrics (BAFTA albert style)
        production = self.repo.get_production(production_id)
        intensity_per_hour = None
        if production.runtime_min and production.runtime_min > 0:
            intensity_per_hour = total_kgco2e / 1000 / (production.runtime_min / 60)
        
        intensity_per_episode = None
        if production.episodes and production.episodes > 0:
            intensity_per_episode = total_kgco2e / 1000 / production.episodes
        
        return ProductionSummary(
            production_id=production_id,
            total_tco2e=round(total_kgco2e / 1000, 3),
            scope_breakdown={k: round(v / 1000, 3) for k, v in scope_totals.items()},
            category_breakdown={k: round(v / 1000, 3) for k, v in category_totals.items()},
            phase_breakdown={k: round(v / 1000, 3) for k, v in phase_totals.items()},
            overall_confidence=round(weighted_confidence, 3),
            budget_variance_percent=round(budget_variance * 100, 1) if budget_variance else None,
            intensity_tco2e_per_hour=round(intensity_per_hour, 3) if intensity_per_hour else None,
            intensity_tco2e_per_episode=round(intensity_per_episode, 3) if intensity_per_episode else None,
            event_count=len(events),
            tier_1_percent=sum(1 for e in events if e.confidence_tier == TIER_1) / len(events) * 100 if events else 0,
            tier_2_percent=sum(1 for e in events if e.confidence_tier == TIER_2) / len(events) * 100 if events else 0,
            tier_3_percent=sum(1 for e in events if e.confidence_tier == TIER_3) / len(events) * 100 if events else 0,
        )
```

---

## 5. API Design (RESTful + Resource-Oriented)

### 5.1 Productions

```
POST   /api/v1/productions              → Create production
GET    /api/v1/productions              → List productions (paginated)
GET    /api/v1/productions/{id}         → Get production + summary
PATCH  /api/v1/productions/{id}         → Update production metadata
DELETE /api/v1/productions/{id}         → Soft delete

GET    /api/v1/productions/{id}/summary → ProductionSummary (aggregated)
GET    /api/v1/productions/{id}/events  → List activity events
POST   /api/v1/productions/{id}/events  → Bulk create events
GET    /api/v1/productions/{id}/budget-variance → Real-time variance report
```

### 5.2 Activity Events

```
POST   /api/v1/events                   → Create single event (auto-calculates)
GET    /api/v1/events/{id}              → Get event with calculation details
PATCH  /api/v1/events/{id}              → Update (triggers recalculation)
DELETE /api/v1/events/{id}              → Delete + recalc production summary

POST   /api/v1/events/bulk              → CSV/JSON bulk import
POST   /api/v1/events/calculate         → Preview calculation (no save)
```

### 5.3 Emission Factors

```
GET    /api/v1/factors                  → List factors (filter by category, region, standard)
GET    /api/v1/factors/{id}             → Get factor details
POST   /api/v1/factors                  → Add custom factor (EPD)
GET    /api/v1/factors/lookup           → Find best factor for activity
                                   Query: ?category=ENERGY&subcategory=diesel_generator&region=UK
```

### 5.4 Documents & OCR

```
POST   /api/v1/documents                → Upload document → S3
GET    /api/v1/documents/{id}           → Get doc + extraction status
POST   /api/v1/documents/{id}/extract   → Trigger LLM extraction
POST   /api/v1/documents/{id}/approve   → Approve extraction → create events
POST   /api/v1/documents/{id}/reject    → Reject + send back to queue
GET    /api/v1/documents/pending-review → Human review queue
```

### 5.5 Forecasting & ML

```
POST   /api/v1/forecast/greenlight      → Predict from production metadata
                                   Body: {genre, budget_band, shoot_days, vfx_intensity, ...}
                                   Response: {predicted_tco2e, interval_lower, interval_upper, confidence, shap}

POST   /api/v1/forecast/impute          → Impute missing category from partial data
GET    /api/v1/forecast/{production_id} → Get all forecasts for production
```

### 5.6 Reporting

```
GET    /api/v1/reports/albert-export/{production_id}  → BAFTA Albert CSV
GET    /api/v1/reports/pdf/{production_id}            → Sustainability report PDF
GET    /api/v1/reports/cdp-template/{production_id}   → CDP disclosure rows
GET    /api/v1/reports/peer-benchmark                 → Compare vs industry averages
```

---

## 6. Data Flow Architecture

### 6.1 Event Ingestion Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI     │────▶│  Validation     │────▶│  Unit       │
│  (Form/CSV) │     │  Endpoint    │     │  (Pydantic)     │     │  Converter  │
└─────────────┘     └──────────────┘     └─────────────────┘     └──────┬──────┘
                                                                         │
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐            │
│  PostgreSQL │◀────│  Save Event  │◀────│  Confidence     │◀───────────┘
│  (events)   │     │  + Result    │     │  Scorer         │
└─────────────┘     └──────────────┘     └─────────────────┘
       │
       ▼
┌─────────────┐
│  Trigger    │────▶ Recalculate ProductionSummary (async via Celery)
│  (PostgreSQL│
│   NOTIFY)   │
└─────────────┘
```

### 6.2 Document Processing Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌─────────────┐
│  Document   │────▶│  S3 Upload   │────▶│  Celery Worker  │────▶│  OCR        │
│  Upload     │     │  (presigned) │     │  (queued)       │     │  (Tesseract │
└─────────────┘     └──────────────┘     └─────────────────┘     │  / Mistral) │
                                                                   └──────┬──────┘
                                                                          │
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐             │
│  Human      │◀────│  Review      │◀────│  LLM Extraction │◀────────────┘
│  Review     │     │  Queue       │     │  (Claude/GPT)   │
│  (UI)       │     │  (<70% conf) │     └─────────────────┘
└──────┬──────┘     └──────────────┘              │
       │                                          │
       └──────────────────────────────────────────┘
              Approve → Create ActivityEvents
```

---

## 7. Database Schema (PostgreSQL)

```sql
-- Core production table
CREATE TABLE productions (
    production_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    type production_type NOT NULL,
    genre genre_type,
    budget_band budget_band,
    runtime_min INTEGER,
    episodes INTEGER DEFAULT 1,
    shoot_days INTEGER,
    cast_count INTEGER,
    crew_count INTEGER,
    vfx_intensity vfx_intensity DEFAULT 'NONE',
    status production_status DEFAULT 'DEVELOPMENT',
    carbon_budget_tco2e DECIMAL(12,4),
    carbon_budget_source budget_source,
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity events (partitioned by production_id for scale)
CREATE TABLE activity_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id UUID NOT NULL REFERENCES productions(production_id) ON DELETE CASCADE,
    phase phase_type NOT NULL,
    scope scope_type NOT NULL,
    category category_type NOT NULL,
    subcategory TEXT NOT NULL,
    value DECIMAL(15,6) NOT NULL,
    unit unit_type NOT NULL,
    kgco2e DECIMAL(15,6) NOT NULL,
    kgco2e_wtt DECIMAL(15,6),
    confidence_tier confidence_tier NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    source_type source_type NOT NULL,
    source_reference TEXT,
    emission_factor_id UUID NOT NULL,
    emission_factor_version TEXT NOT NULL,
    location_id UUID,
    grid_region TEXT,
    recorded_by UUID NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    notes TEXT,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    calculation_method TEXT NOT NULL
) PARTITION BY HASH (production_id);

-- Emission factors (versioned, immutable)
CREATE TABLE emission_factors (
    factor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard factor_standard NOT NULL,
    category category_type NOT NULL,
    subcategory TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    factor_value DECIMAL(15,8) NOT NULL,
    unit unit_type NOT NULL,
    scope scope_type NOT NULL,
    region TEXT NOT NULL DEFAULT 'Global',
    country_code CHAR(2),
    grid_intensity_g_co2_kwh DECIMAL(10,4),
    valid_from DATE NOT NULL,
    valid_to DATE,
    version TEXT NOT NULL,
    source_url TEXT,
    description TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    radiative_forcing_multiplier DECIMAL(3,2) DEFAULT 1.0,
    wtt_factor DECIMAL(15,8),
    UNIQUE (standard, category, subcategory, region, version)
);

-- Indexes for fast lookups
CREATE INDEX idx_factors_lookup ON emission_factors(category, subcategory, region, is_active);
CREATE INDEX idx_events_production ON activity_events(production_id, category);
CREATE INDEX idx_events_scope ON activity_events(production_id, scope);
CREATE INDEX idx_events_confidence ON activity_events(confidence_tier);

-- Materialized view for production summaries (refreshed on event changes)
CREATE MATERIALIZED VIEW production_summaries AS
SELECT 
    production_id,
    SUM(kgco2e) / 1000.0 AS total_tco2e,
    SUM(CASE WHEN scope = 'SCOPE_1' THEN kgco2e ELSE 0 END) / 1000.0 AS scope_1_tco2e,
    SUM(CASE WHEN scope = 'SCOPE_2' THEN kgco2e ELSE 0 END) / 1000.0 AS scope_2_tco2e,
    SUM(CASE WHEN scope = 'SCOPE_3' THEN kgco2e ELSE 0 END) / 1000.0 AS scope_3_tco2e,
    SUM(kgco2e * confidence_score) / NULLIF(SUM(kgco2e), 0) AS weighted_confidence,
    COUNT(*) AS event_count,
    COUNT(*) FILTER (WHERE confidence_tier = 'TIER_1') * 100.0 / NULLIF(COUNT(*), 0) AS tier_1_pct
FROM activity_events
GROUP BY production_id;

CREATE UNIQUE INDEX idx_summary_prod ON production_summaries(production_id);
```

---

## 8. Seed Data Strategy

### Phase 1: Core DEFRA Factors (UK-focused, like BAFTA albert)

| Category | Subcategory | Unit | Factor Value | Scope |
|----------|-------------|------|--------------|-------|
| ENERGY | diesel_generator | kgCO₂e/L | 2.68 | SCOPE_1 |
| ENERGY | hvo_fuel | kgCO₂e/L | 0.20 | SCOPE_1 |
| ENERGY | grid_electricity_uk | kgCO₂e/kWh | 0.207 | SCOPE_2 |
| ENERGY | natural_gas | kgCO₂e/kWh | 0.182 | SCOPE_1 |
| TRANSPORT | short_haul_flight | kgCO₂e/km | 0.158 | SCOPE_3 |
| TRANSPORT | long_haul_flight | kgCO₂e/km | 0.195 | SCOPE_3 |
| TRANSPORT | medium_car_petrol | kgCO₂e/km | 0.192 | SCOPE_1 |
| TRANSPORT | medium_car_diesel | kgCO₂e/km | 0.171 | SCOPE_1 |
| MATERIALS | lumber_general | kgCO₂e/kg | 0.50 | SCOPE_3 |
| WASTE | landfill_general | kgCO₂e/kg | 0.50 | SCOPE_3 |
| WASTE | recycling_mixed | kgCO₂e/kg | 0.02 | SCOPE_3 |
| CATERING | beef_average | kgCO₂e/kg | 60.0 | SCOPE_3 |
| CATERING | chicken_average | kgCO₂e/kg | 6.1 | SCOPE_3 |
| WATER | water_supply | kgCO₂e/m3 | 0.15 | SCOPE_3 |

### Phase 2: Regional Expansion
- EPA factors for US productions
- Country-specific electricity factors (309 like BAFTA albert)
- Grid intensity time-series from Electricity Maps

### Phase 3: Benchmark Database
- Studio energy benchmarks (kWh/m²/day by stage size)
- Edit suite benchmarks (2.999 kWh/hour for post)
- Per-genre, per-budget carbon benchmarks

---

## 9. Business Rules & Validations

```python
class EventValidator:
    """Pydantic validators for ActivityEvent creation."""
    
    RULES = {
        # Fuel values must be positive
        "fuel_positive": lambda e: e.value > 0 if "fuel" in e.subcategory else True,
        
        # Distance values must be positive
        "distance_positive": lambda e: e.value > 0 if e.category == TRANSPORT else True,
        
        # Grid electricity must have region for accurate intensity
        "electricity_region": lambda e: e.grid_region is not None 
            if e.subcategory == "grid_electricity" else True,
        
        # Air travel radiative forcing must use 1.7×
        "air_travel_rf": lambda e: e.factor.radiative_forcing_multiplier == Decimal("1.7")
            if "air" in e.subcategory else True,
        
        # Confidence score must match tier
        "confidence_consistency": lambda e: (
            (e.confidence_tier == TIER_1 and e.confidence_score >= 0.85) or
            (e.confidence_tier == TIER_2 and 0.60 <= e.confidence_score < 0.85) or
            (e.confidence_tier == TIER_3 and e.confidence_score < 0.60)
        ),
        
        # Scope must match factor scope
        "scope_matches_factor": lambda e: e.scope == e.factor.scope,
    }
```

---

## 10. Error Handling & Edge Cases

| Scenario | Handling |
|----------|----------|
| No emission factor found for activity | Return 422 with suggestion list; allow custom factor creation |
| Negative activity value | Reject with clear error; only waste diversion can be negative |
| Duplicate event (same source ref) | Idempotent upsert based on source_reference + production_id |
| Factor expired (valid_to passed) | Warning flag on calculation; suggest updated factor |
| Unit mismatch (miles vs km) | Auto-convert using standard constants; log conversion |
| Missing grid region for electricity | Fallback to country average; mark confidence lower |
| Bulk CSV with partial errors | Return detailed row-level errors; save valid rows |
| Production has zero events | Return empty summary with 0.0 values; don't error |

---

## 11. Implementation Order (Backend-First)

### Week 1: Foundation
- [ ] Scaffold FastAPI project with Pydantic v2, SQLAlchemy 2.0, Alembic
- [ ] Design full database schema + migrations
- [ ] Create domain models (Production, ActivityEvent, EmissionFactor)
- [ ] Seed emission factor table with 50 core DEFRA factors

### Week 2: Core Calculation Engine
- [ ] Implement `CalculationEngine.calculate()`
- [ ] Implement `UnitConverter` with all production-relevant conversions
- [ ] Implement `ScopeClassifier` with GHG Protocol rules
- [ ] Write comprehensive unit tests for calculation accuracy

### Week 3: Confidence Scoring & Aggregation
- [ ] Implement `ConfidenceScorer` with tier logic
- [ ] Implement `ProductionAggregator` with all rollup queries
- [ ] Create materialized view + refresh trigger
- [ ] API endpoints: `POST /events`, `GET /productions/{id}/summary`

### Week 4: Bulk Import & Validation
- [ ] CSV parser with template validation
- [ ] Bulk create endpoint with row-level error reporting
- [ ] Document upload → S3 + metadata record
- [ ] Input validation rules engine

### Week 5: Forecasting (ML Integration)
- [ ] Greenlight predictor model (XGBoost) training script
- [ ] Model registry (MLflow-lite or filesystem)
- [ ] `POST /forecast/greenlight` endpoint
- [ ] SHAP explainability serialization

### Week 6: Reporting & Export
- [ ] BAFTA Albert CSV formatter
- [ ] PDF report generation service
- [ ] CDP/ISSB template population
- [ ] Peer benchmark comparison queries

---

*This backend logic plan gives you a complete, research-backed foundation. Every formula, every classification rule, and every data model is grounded in GHG Protocol standards and BAFTA albert's proven calculator methodology. The next step is to scaffold the actual Python/FastAPI codebase.*
