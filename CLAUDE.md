# Terra   — Sustainability Platform

A domain-agnostic carbon accounting platform (first vertical: **film & TV production**). Tracks activity events → emission factors → tCO₂e; predicts pre-production footprint ("Greenlight Forecast"); flags anomalies.

---

## Repository layout

```
backend/           FastAPI + SQLAlchemy + Alembic (SQLite dev, Postgres prod)
  app/
    api/           Route modules: productions, events, factors, ml
    services/      calculation_engine, confidence_scorer, csv_importer, scope_classifier
    models.py      ORM: Production, ActivityEvent, EmissionFactor, Document
    schemas.py     Pydantic I/O schemas
    main.py        FastAPI entrypoint; mounts routers under /api/v1
  alembic/         Migrations
  tests/           Pytest suite
  seed_emission_factors.py

ml_engine/         Standalone ML package
  greenlight_predictor.py   Pre-production CO2e estimator
  anomaly_detector.py       Outlier detection on events
  category_imputer.py       Fills missing scope/category
  features.py, pipeline.py, schemas.py, demo.py

frontend/          Vite + React 19 + TypeScript + Tailwind v4 + React Router 7
  src/
    App.tsx                 Routes
    components/Layout.tsx   Top-nav shell
    pages/                  ProductionsList, ProductionDetail, UploadCSV, GreenlightForecast
    api.ts, types.ts
  dependencies: lucide-react (icons), recharts (charts)

ml_models/         Serialized trained models
demo_models/       Demo-ready bundles
test_data/         Sample CSVs & fixtures
uireferences/      Design inspiration (see UI section)

Top-level docs:
  BACKEND_LOGIC_PLAN.md
  DATASETS_AND_TEST_DATA.md
  DOMAIN_TEMPLATE_DESIGN.md
  END_TO_END_BUILD_PLAN.md
  netflix_production_sustainability_framework.html
```

---

## Domain model (core tables)

- **Production**   — title, type, genre, budget_band, shoot_days, locations (JSON), cast/crew counts, vfx_intensity, status, carbon_budget_tco2e. Keyed by `production_id`; partitioned by `domain` so the same schema serves non-film verticals later.
- **ActivityEvent**   — phase, scope (1/2/3), category, subcategory, value+unit → kgco2e (+ wtt). Carries `confidence_tier`, `confidence_score`, `source_type`, `emission_factor_id`+`version` for audit.
- **EmissionFactor**   — reference library (seeded via `seed_emission_factors.py`).
- **Document**   — attachments tied to a production.

## Backend conventions

- All routes under `/api/v1/...`.
- `Base.metadata.create_all` runs on startup for dev; use Alembic for prod schema changes.
- CORS origins from `app.config.settings.cors_origins`.
- Services (`app/services/*`) hold business logic; keep API handlers thin.
- Run dev: `uvicorn app.main:app --reload` from `backend/`.
- Run tests: `pytest` from `backend/`.

## Frontend conventions

- Tailwind v4 via `@tailwindcss/vite` (no `tailwind.config.js` needed for v4).
- Single `Layout` wraps all routes. Pages live in `src/pages/`, shared UI in `src/components/`.
- API calls centralized in `src/api.ts`; types in `src/types.ts`.
- Icon set: `lucide-react`. Charts: `recharts`.
- Run dev: `npm run dev` from `frontend/`. Build: `npm run build`.

## ML engine

- Imported as a package (`ml_engine.*`) by the backend ML router (`app/api/ml.py`).
- Models are loaded from `ml_models/` (prod) or `demo_models/` (demo).
- Standalone demo: `python -m ml_engine.demo`.

---

## UI direction (in-progress redesign)

Two reference inspirations live in `uireferences/`:

1. **Visualboard (green dashboard)**   — left sidebar nav, soft rounded cards, pastel green accents, an illustrated hero card with a friendly 3D character, mini KPI bar charts, product list table. Cheerful, consumer-friendly, data-dense.
2. **Zentra (property dashboard)**   — purple/lavender palette, sky-backdrop illustration framing the app card, gradient-filled feature KPI, 3D isometric building vignettes, clean cashflow bars and a map card.

**Terra's chosen direction:** fuse the two   — take Visualboard's green palette (sustainability-native) and card rhythm, with Zentra's airy ambient backdrop and 3D clay-rendered illustrations. Tone: warm, optimistic, credible   — not "corporate ESG dashboard."

### Visual system

- **Palette**
  - Primary: emerald `#10B981`, deep forest `#065F46`
  - Accent: warm amber `#F59E0B` (for alerts / over-budget)
  - Neutrals: slate-50 → slate-900
  - Ambient backdrop: soft sky gradient (pale green → cream) with faint cloud/leaf motifs
- **Surfaces**
  - Cards: `rounded-2xl`, white, shadow `0 8px 24px -12px rgba(16,24,40,0.08)`
  - Inner KPI panels: subtle gradient fills for the "hero" metric, flat white for secondary
  - Sidebar: pill-shaped active state, 240px wide, light-mode default
- **Typography**: Inter (UI) + a friendly display face (General Sans / Cabinet Grotesk) for hero numbers.
- **Charts**: recharts with rounded bar caps, soft gradients, minimal gridlines, emerald/amber duotone.
- **Illustrations**: 3D clay-render style   — matte, soft shadows, rounded geometry, small scale props (trees, cameras, clapboards, solar panels).

### Information architecture (proposed)

```
Sidebar
  GENERAL
    Dashboard (overview)
    Productions
    Events (activity log)
    Greenlight Forecast
    Anomalies
  DATA
    Upload CSV
    Emission Factors
  SETTINGS
    Team, Integrations, Billing
Top bar: search, notifications, user menu
```

### Key screens to design

1. **Dashboard**   — Hero card ("Your footprint this quarter"), 4 KPI tiles (Total tCO₂e, vs Budget, Scope mix, Active productions), emissions-by-phase chart, recent events table, upcoming milestones card.
2. **Production detail**   — Production hero with 3D clay illustration contextual to type (film set / TV studio / doc shoot), scope-1/2/3 donut, phase breakdown bars, events table, confidence distribution.
3. **Greenlight Forecast**   — Input card (title, type, budget band, shoot days…), predicted tCO₂e with confidence band, comparable productions, reduction-lever suggestions.
4. **Upload CSV**   — Drop zone with clay-illustrated "import" mascot, preview table, validation errors, import summary.

---

## 3D clay-style illustration prompts

Use these prompts with an image model (Midjourney v6, Flux, SDXL). Common style suffix   — append to every prompt:

> *3D clay render, matte plasticine finish, soft studio lighting, gentle ambient occlusion, rounded geometry, pastel palette anchored in emerald green and cream with warm amber accents, subtle grain, isometric or three-quarter view, white or pale-green seamless background, no text, no logos, centered composition, high detail, cinema4d + octane look, Bella Illustration / Oleg Beresnev style, 4k*

### 1. Dashboard hero   \"Planet under care"
> A cheerful 3D clay-rendered globe of Earth, its forests and oceans visibly healthy, with tiny solar panels, wind turbines, and a small film camera on a tripod orbiting it on a soft emerald ring; a friendly rounded character in a director's vest gently holds a leaf up to the globe. [+ style suffix]

### 2. Productions list   \"Film set on a green hill"
> A miniature 3D clay film set on a rounded grassy hill: a matte clapboard, a small camera on a dolly, two tiny folding chairs, a soft boom mic, surrounded by three stylized trees and a cotton cloud; warm sunlight from upper-left, long soft shadows. [+ style suffix]

### 3. Greenlight Forecast   \"Crystal ball of carbon"
> A glossy clay crystal ball resting on a rounded pedestal, inside the ball a tiny translucent film studio with a downward-trending emissions graph made of stacked green cylinders; a small sprout grows out of the top of the pedestal; amber glow from within the ball. [+ style suffix]

### 4. Upload CSV   \"Data courier mascot"
> A round, friendly clay mascot (egg-shaped body, tiny arms, big smile) carrying an oversized green spreadsheet document twice its size toward a glowing upload portal; floating rows of data flow into the portal as soft green ribbons. [+ style suffix]

### 5. Anomaly / alerts   \"Detective leaf"
> A chubby clay character wearing a tiny deerstalker hat and holding a magnifying glass, inspecting a single oversized clay leaf that has one amber warning dot on it; scattered tiny data cards around its feet. [+ style suffix]

### 6. Empty state / onboarding
> A single small clay sprout growing out of a rounded pile of soft green soil, a tiny watering can tipped toward it releasing three droplets; lots of negative space above. [+ style suffix]

### 7. Sidebar / login decoration   \"Sustainable city vignette"
> An isometric 3D clay micro-city: one sound stage with a rooftop solar array, one small apartment with a green roof, two trees, one electric van charging, one wind turbine in the back; all rounded, toy-like. [+ style suffix]

### 8. KPI hero tile background   \"Leaf swirl"
> An abstract swirl of three oversized clay leaves in varying emerald tones, arranged in a gentle spiral, soft depth of field, plenty of negative space on the right for overlaying a large number. [+ style suffix]

### 9. Scope 1/2/3 explainer   \"Three stacked worlds"
> Three small stacked clay planets connected by soft ribbons: bottom one with a fuel pump and truck (Scope 1), middle one with a power line and lightning bolt (Scope 2), top one with a shopping bag and airplane (Scope 3); unified warm lighting. [+ style suffix]

### 10. 404 / error
> A clay character scratching its head next to a bent film reel, a single question-mark-shaped cloud floating above; soft pastel background. [+ style suffix]

### Tips when generating
- Always fix seed + aspect ratio per placement: hero = 16:9, sidebar vignette = 4:5, KPI background = 3:2, mascots = 1:1.
- Ask for **transparent PNG** or pure white background; composite onto Terra's pale-green card background in CSS.
- Keep characters **faceless-friendly** (dots for eyes, no mouths) to sidestep uncanny-valley and keep the set cohesive.
- Re-roll with `--style raw` (MJ) or a low guidance scale (Flux ~3.5) if the model over-renders realistic materials.

---

## Coding guardrails for this repo

- Keep the schema **domain-agnostic**: new verticals must reuse `Production` + `ActivityEvent` with a new `domain` value, not a new table.
- Never persist raw emission calculations without `emission_factor_id` + `emission_factor_version`   — auditability is non-negotiable.
- Frontend: no new CSS frameworks. Stay on Tailwind v4 + recharts + lucide.
- Charts should prefer emerald primary / amber warn / slate neutral. No rainbow categorical palettes.
