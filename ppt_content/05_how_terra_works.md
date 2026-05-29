# Slide 5 — How Terra Works (Platform Mechanics)

## Slide Title
From Activity to Insight in Four Steps

## The Universal Formula
```
CO₂e (kg) = Activity Data × Emission Factor × Grid Intensity Modifier
```

## Step-by-Step Flow

### Step 1 — Capture the Atom
**"What happened?"**
- Manual form entry (fuel, travel, energy, waste, catering, materials)
- CSV bulk upload (200 events in one drop)
- Document upload → OCR/LLM extraction (invoice → structured event)
- Free-text: *"45 litres of diesel for Generator B at Pinewood"* → parsed automatically

### Step 2 — Look Up the Science
**"How bad is it?"**
- Emission Factor Registry: DEFRA (UK), EPA (US), GHG Protocol, BAFTA Albert
- 50+ core factors seeded: diesel (2.546 kgCO₂e/L), grid electricity (0.207 kgCO₂e/kWh), beef (60 kgCO₂e/kg)...
- Grid intensity by region (UK, California, Germany — real-time via Electricity Maps)
- Special rules: air travel gets 1.7× radiative forcing multiplier

### Step 3 — Calculate with Confidence
**"How sure are we?"**
| Tier | Source | Confidence | Error Band |
|------|--------|------------|------------|
| **Tier 1** | Meter readings, weighed receipts, IoT | 90-99% | ±5% |
| **Tier 2** | Invoices, spend-based, benchmarks | 65-89% | ±15-25% |
| **Tier 3** | ML-imputed from project metadata | 40-64% | ±30-50% |

### Step 4 — Aggregate & Act
**"What does it mean?"**
- Scope breakdown (1 / 2 / 3)
- Category breakdown (Energy, Transport, Catering, Waste...)
- Phase breakdown (Development → Pre-Production → Production → Post → Distribution)
- Variance vs. carbon budget
- Intensity metrics (tCO₂e per broadcast hour, per m² built, per episode)

## Visual Direction
- Horizontal flow diagram with 4 connected clay-render cards
- Card 1: Tiny hand writing in a notebook (Capture)
- Card 2: Magnifying glass over a formula (Lookup)
- Card 3: Confidence meter dial (Calculate)
- Card 4: Dashboard with charts (Act)
- Connecting arrows as soft green ribbons

## Speaker Notes
Walk through the loop slowly. The magic is that every single step is auditable. When an auditor asks "where did this 2.68 kgCO₂e per litre come from?" you point to DEFRA-2024-v1, valid from July 2024, with a source URL. When they ask "how confident are you?" you show them Tier 1, 95% score, meter reading #4521. This isn't black-box sustainability. It's accounting-grade transparency.
