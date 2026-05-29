# Slide 7 — The Brain: How Terra Learns from Data

## Slide Title
Trained on Reality. Learning with Every Project.

## The ML Engine Stack
Terra's intelligence layer is **domain-agnostic by design**. The models don't know what "VFX" means — they just see numbers, patterns, and deviations.

```
┌─────────────────────────────────────────┐
│         ML ENGINE (ml_engine/)          │
├─────────────────────────────────────────┤
│  Greenlight Predictor  │  XGBoost       │
│  Anomaly Detector      │  Z-Score + TS  │
│  Category Imputer      │  Statistical   │
│  AI Copilot            │  LLM (GPT-4o)  │
│  AI Strategist         │  LLM (Claude)  │
└─────────────────────────────────────────┘
```

## Model 1 — Greenlight Predictor (Pre-Production Forecasting)
**Question:** *"Before we shoot a single frame, how much carbon will this production emit?"*

**How it works:**
1. **Input** (project metadata): genre, budget band, shoot days, locations, cast/crew count, VFX intensity
2. **Feature engineering** → generic feature vector: [project_type, scale_band, duration, headcount, complexity, output_units, output_size]
3. **XGBoost regressor** trained on synthetic + historical benchmarks (SPA, BAFTA albert, Netflix ESG)
4. **Output**: predicted total tCO₂e + prediction interval [lower, upper] + confidence score
5. **Explainability**: SHAP attribution — "shoot_days contributed 32%, vfx_intensity 28%"

**Training Data Sources:**
| Source | Records | Type |
|--------|---------|------|
| BAFTA albert | 2,500+ footprints | Real (UK) |
| SPA / Green Production Alliance | 159+ productions | Real (US) |
| Netflix ESG Reports | 6 years | Aggregated |
| Synthetic Generator | Unlimited | Benchmark-driven with ±20% noise |

**Sample Prediction:**
```
Input:  Action film, $10-50M, 45 shoot days, 3 locations, HIGH VFX
Output:  Predicted 487 tCO₂e  [380 — 620]  ·  Confidence: 78%
        SHAP: shoot_days (0.32) | vfx_intensity (0.28) | budget_band (0.19)
```

## Model 2 — Anomaly Detector (Live Monitoring)
**Question:** *"Is today's fuel usage normal for this phase of production?"*

**How it works:**
- Rolling-window z-score detection on time-series of kgCO₂e
- Flags spikes/drops > 2σ (medium alert) or > 3σ (high alert)
- Example: "Diesel usage is 47% above the 14-day rolling average. Check Generator B."

## Model 3 — Category Imputer (Gap Filling)
**Question:** *"We missed hotel data for Week 2. What was it likely?"*

**How it works:**
- Uses known categories + project metadata to statistically impute missing values
- Every imputed value carries Tier 3 confidence (40-64%)
- Never pretends to be measured data

## Model 4 — AI Copilot & Strategist (Conversational Intelligence)
**Question:** *"How do I explain this spike to my producer?"*

**How it works:**
- LLM-powered (GPT-4o / Claude via LiteLLM) with production context
- Can parse free-text events: *"45L diesel, Pinewood, Generator B"* → structured ActivityEvent
- Generates executive summaries, reduction plans, and anomaly explanations
- Streaming responses for real-time chat feel

## The Learning Loop
```
Prediction → Production Happens → Real Events Logged → Actual vs Predicted
      ↑___________________________________________________________↓
                         Model Retrains Nightly (Celery batch job)
```

## Visual Direction
- A 3D clay-render "crystal ball" with a tiny film studio inside and a downward-trending emissions graph
- Floating data ribbons flowing into the crystal ball
- Small SHAP bar chart visualisation beside it
- A mini timeline showing: Predict → Track → Compare → Retrain

## Speaker Notes
Here's where Terra becomes more than a calculator. The Greenlight Predictor is like a carbon meteorologist: give it the script metadata, and it forecasts the storm before clouds gather. The anomaly detector is your early warning system. The AI strategist is the person you wish you had sitting next to you in the production office at 11 PM, explaining why the numbers look weird. And every prediction gets better because every production that finishes becomes training data for the next one.
