# Slide 6 — How Things Are Defined (The Terra Architecture)

## Slide Title
A Universal Language for Carbon — Built to Scale Across Any Domain

## The Four-Entity Core
Everything in Terra reduces to four entities. This is intentional. It makes Terra **domain-agnostic**.

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   PROJECT   │────▶│  ACTIVITY EVENT │────▶│  EMISSION FACTOR│────▶│  CALCULATION │
│  (anything) │     │  (what happened)│     │  (kgCO₂e/unit)  │     │  (result)    │
└─────────────┘     └─────────────────┘     └─────────────────┘     └──────────────┘
```

## Entity Definitions

### 1. Project
The container. In film it's a "Production." In construction it's a "Building Site." In logistics it's a "Delivery Route."
- Metadata: type, scale, duration, headcount, complexity
- Carbon budget (predicted or manual)
- Lifecycle: Development → Pre-Production → Production → Post → Distribution → Wrapped

### 2. Activity Event
**The atomic unit.** Every litre, kWh, km, kg becomes one row.
- `phase`: When did it happen?
- `scope`: 1 (direct), 2 (purchased energy), 3 (value chain)
- `category` & `subcategory`: What kind of activity?
- `value` + `unit`: How much?
- `kgco2e`: Computed result
- `confidence_tier` + `confidence_score`: How trustworthy?
- `source_type` + `source_reference`: Where did this come from?

### 3. Emission Factor
The scientific lookup table. Immutable. Versioned. Auditable.
- `standard`: DEFRA, EPA, GHG Protocol, BAFTA Albert, custom EPD
- `factor_value`: kgCO₂e per unit
- `region`: UK, US, EU, Global
- `valid_from` / `valid_to`: Time-bounded accuracy
- `radiative_forcing_multiplier` / `wtt_factor`: Scientific modifiers

### 4. Calculation Result
The output. Always reproducible. Always traceable.
- Base kgCO₂e + optional WTT addition
- Full factor ID + version used
- Calculation method + timestamp

## Domain Mapping (The Same Engine, Any Industry)

| Film/TV | Construction | Logistics | Generic |
|---------|-------------|-----------|---------|
| Production | Building Site | Delivery Route | Project |
| Genre | Building Type | Route Type | Project Type |
| Budget Band | Floor Area Band | Stop Count | Scale Band |
| Shoot Days | Construction Months | Route Days | Duration |
| Cast/Crew | Worker Headcount | Drivers | Headcount |
| VFX Intensity | LEED Level | Refrigerated? | Complexity |
| tCO₂e/hour | tCO₂e/m² | tCO₂e/ton-mile | Intensity |

## Visual Direction
- Clean entity-relationship diagram with rounded boxes
- Film icons on the left → generic labels on the right
- A small toggle switch animation: "Film Mode" ↔ "Construction Mode" ↔ "Logistics Mode"
- Colour code: Project (emerald), Event (sky blue), Factor (amber), Calculation (slate)

## Speaker Notes
This is the architecture slide. The key insight: we didn't build a film tool that happens to work for construction. We built a universal carbon kernel. The film-specific words — production, genre, shoot days, VFX — are just one skin on top of a generic engine. Swap the YAML config, and Terra becomes a construction carbon tracker. Or a logistics tracker. Or a corporate sustainability platform. That's the atomic power: one core, infinite domains.
