# Production Sustainability Intelligence Platform
## End-to-End Build Plan

> **Derived from:** Netflix Production Sustainability Framework  
> **Goal:** Transform the conceptual framework into a working, deployable product.  
> **Philosophy:** Ship a focused MVP that proves value, then expand. Don't build the entire 24-month enterprise stack on day one.

---

## 1. Product Definition

### What We're Building
A **web-based Production Sustainability Intelligence Platform** that enables production teams (PMs, UPMs, sustainability consultants) to:

1. **Budget carbon at greenlight**   — Predict emissions from script metadata before shooting begins
2. **Track emissions live**   — Log daily activity data (fuel, travel, waste, energy) and see variance vs. budget
3. **Calculate with confidence**   — Apply the tiered confidence model (Tier 1 measured → Tier 2 benchmark → Tier 3 ML-imputed)
4. **Generate audit-ready reports**   — Export Albert/PEAR-compatible certification packages
5. **Run the OED playbook**   — Get actionable, department-specific reduction recommendations

### What We're NOT Building (Yet)
- Full real-time IoT streaming ingestion (start with manual entry + CSV upload)
- Graph Neural Network supply-chain propagation (start with lookup tables)
- Multi-tenant enterprise SaaS with RBAC (start with single-org auth)
- Custom LLM training (use API-based extraction with prompt engineering)

### Target User Personas
| Persona | Role | Primary Need |
|---------|------|-------------|
| Green PM | Sustainability lead | Track, report, certify |
| UPM | Unit production manager | Budget, variance alerts, course-correct |
| Line Producer | Financial control | Cost-carbon trade-offs, vendor scorecards |
| ESG Analyst | Corporate reporting | Aggregate, benchmark, disclose |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Dashboard   │  │   Carbon     │  │   Report     │  │   OED        │ │
│  │  (Analytics) │  │   Calculator │  │   Generator  │  │   Playbook   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│                         React + TypeScript + Tailwind                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                   │
│                         FastAPI (Python)                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Productions │  │   Emissions  │  │   ML         │  │   Reports    │ │
│  │  CRUD        │  │   Calculation│  │   Inference  │  │   Export     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Carbon      │  │   Confidence │  │   Document   │  │   Forecast   │ │
│  │  Engine      │  │   Scorer     │  │   Extractor  │  │   Service    │ │
│  │  (emission   │  │  (tier calc) │  │  (LLM OCR)   │  │  (XGBoost)   │ │
│  │   factors)   │  │              │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  PostgreSQL  │  │   S3/MinIO   │  │   Qdrant /   │  │   Redis      │ │
│  │  (structured)│  │   (files)    │  │   pgvector   │  │   (cache)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tech Stack (MVP)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Frontend** | React 18 + TypeScript + Tailwind CSS + Recharts | Fast UI dev, great charting, matches existing design language |
| **Backend** | FastAPI + Pydantic + SQLAlchemy | Python-native ML integration, auto-generated OpenAPI, async |
| **ML Runtime** | scikit-learn + XGBoost + LiteLLM | No GPU needed for MVP, swaps to hosted LLM APIs |
| **Database** | PostgreSQL 15+ (with pgvector for RAG) | Single DB handles structured + vector in MVP |
| **File Store** | S3-compatible (MinIO for local, S3 for prod) | Receipts, PDFs, exports |
| **Cache / Queue** | Redis | Session cache, background job queue |
| **Background Jobs** | Celery + Redis | Async document processing, report generation |
| **Auth** | OAuth2 + JWT (or Clerk/Auth0 for speed) | Production-grade auth without building it |
| **Deployment** | Docker Compose (local) → AWS/GCP (prod) | Standard containers, portable |

---

## 3. Core Features & Modules

### Module A: Production Management
- Create production with metadata (title, genre, budget band, shoot days, locations, cast/crew count, VFX intensity)
- Auto-generate carbon budget prediction at greenlight
- Production lifecycle states: Development → Pre-Production → Production → Post → Distribution → Wrapped

### Module B: Data Ingestion & Activities
**Structured Entry:**
- Forms for fuel/energy, travel, materials, waste, catering, cloud/VFX
- CSV bulk upload with template validation
- Support for unit conversions (L → kgCO₂e, kWh → kgCO₂e)

**Unstructured Processing (V1):**
- Upload invoices, fuel receipts, travel manifests
- OCR + LLM extraction to structured data (using GPT-4o / Claude Haiku via LiteLLM)
- Human review queue for low-confidence extractions (< 70%)

### Module C: Carbon Calculation Engine
**Emission Factor Registry:**
- Built-in factors: DEFRA (UK), EPA (US), GHG Protocol, BAFTA Albert
- Grid intensity by region (Electricity Maps API integration)
- User-custom factors for specific vendors

**Calculation Pipeline:**
```
Activity Data + Unit → Lookup Emission Factor × Grid Intensity → kgCO₂e
                                    ↓
                        Apply Confidence Tier
                        Tier 1: Direct measurement (±5%)
                        Tier 2: Benchmark/spend-based (±15-25%)
                        Tier 3: ML-imputed (±30-50%)
```

**Scope Classification:**
- Auto-classify into Scope 1 / 2 / 3 based on activity type
- Per-department rollups (Transport, Energy, Materials, Catering, Waste, Post/VFX)

### Module D: ML Forecasting (MVP)
**Greenlight Predictor:**
- XGBoost regressor trained on synthetic + historical production data
- Input: genre, budget_band, shoot_days, locations, vfx_intensity
- Output: predicted total tCO₂e with prediction interval
- SHAP attribution for explainability

**Imputation Engine:**
- When data is missing, use production metadata to impute category emissions
- Confidence score attached to every imputed value

### Module E: Confidence Scoring
Implement the tiered confidence model from the framework:
- **Tier 1 (High):** Direct meter readings, weighed receipts, IoT streams → Score: 95%
- **Tier 2 (Medium):** Spend-based calculation using emission factors → Score: 75%
- **Tier 3 (Low):** Benchmark or ML-imputed from metadata → Score: 55%

**Overall Production Score:**
```
Confidence = Σ(category_tCO₂e × category_confidence) / Σ(category_tCO₂e)
```
Visualized as a progress bar with color coding (green ≥80%, amber 60-80%, red <60%)

### Module F: OED Playbook Engine
**Optimise · Electrify · Decarbonise**
- Rule-based recommendation engine that suggests actions based on production data
- Department-specific playbooks (Transport, Energy, Art, Catering, Post)
- Impact estimation: "Switch to HVO → -X tCO₂e → $Y cost"

### Module G: Reporting & Certification
**Dashboards:**
- Real-time total footprint vs. budget
- Scope breakdown (1/2/3)
- Department-level breakdown
- Trend over production phases

**Exports:**
- BAFTA Albert-compatible CSV export
- PDF Sustainability Report (auto-generated)
- CDP / ISSB IFRS S2 disclosure templates

---

## 4. Data Model (Core Entities)

```python
# Production
production_id, title, genre, budget_band, shoot_days, 
locations[], vfx_intensity, status, carbon_budget_tco2e, created_at

# ActivityEvent (the core fact table)
event_id, production_id, phase, activity_type, scope,
category, subcategory, value, unit, emission_factor_id,
kgco2e, confidence_tier, confidence_score, source_type,
metadata JSONB, recorded_by, recorded_at

# EmissionFactor
factor_id, category, subcategory, region, factor_value, 
unit_denominator, source_standard (DEFRA/EPA/GHGP),
valid_from, valid_to

# Document (for unstructured processing)
doc_id, production_id, doc_type, s3_path, ocr_status,
extracted_data JSONB, confidence_score, review_status

# Vendor
vendor_id, name, category, location, green_certified,
epd_available, avg_emission_factor, scorecard JSONB

# Forecast / Model Run
run_id, production_id, model_version, prediction_tco2e,
interval_lower, interval_upper, shap_attribution JSONB,
created_at
```

---

## 5. Implementation Roadmap

### Phase 0: Foundation (Weeks 1-2)
- [ ] Scaffold FastAPI + React project with Docker Compose
- [ ] Set up PostgreSQL with pgvector, Redis, MinIO
- [ ] Auth system (JWT or Clerk integration)
- [ ] CI/CD pipeline (GitHub Actions → build + test)
- [ ] Seed emission factor database (DEFRA + EPA core categories)

### Phase 1: Core Tracking (Weeks 3-5)
- [ ] Production CRUD + metadata forms
- [ ] Activity event entry forms (all 6 categories)
- [ ] CSV bulk upload with validation
- [ ] Carbon calculation engine (Tier 1 & 2)
- [ ] Basic dashboard: total footprint, scope pie chart, vs. budget

### Phase 2: Intelligence (Weeks 6-8)
- [ ] Greenlight predictor model (XGBoost) + training pipeline
- [ ] Confidence scoring engine (Tier 1/2/3 logic)
- [ ] Confidence calculator UI (interactive, like in the HTML framework)
- [ ] OED playbook rule engine + recommendations UI
- [ ] SHAP explainability integration

### Phase 3: Document AI (Weeks 9-11)
- [ ] Document upload → S3
- [ ] OCR pipeline (Tesseract / Mistral OCR)
- [ ] LLM extraction via LiteLLM (Claude Haiku / GPT-4o-mini)
- [ ] Human review queue for low-confidence extractions
- [ ] Auto-create ActivityEvents from approved extractions

### Phase 4: Reporting & Polish (Weeks 12-14)
- [ ] Albert-compatible CSV export
- [ ] PDF report generator (WeasyPrint or Playwright)
- [ ] Advanced dashboards: per-department trends, variance analysis
- [ ] Production lifecycle workflow (state machine)
- [ ] User onboarding + demo data

### Phase 5: Harden & Deploy (Weeks 15-16)
- [ ] Performance testing (1000+ productions, 100k+ events)
- [ ] Security audit + input sanitization
- [ ] Cloud deployment (AWS ECS / GCP Cloud Run)
- [ ] Monitoring (Sentry + basic logging)
- [ ] Documentation + API reference

---

## 6. Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| **Build vs. Buy Auth** | Buy (Clerk/Auth0) | Don't build auth in MVP |
| **LLM Strategy** | API-first (LiteLLM) | No model hosting overhead; swap providers easily |
| **Vector DB** | pgvector in Postgres | One less service to run in MVP; migrate to Qdrant/Pinecone at scale |
| **ML Training** | Offline batch (nightly) | No real-time training complexity; scheduled Celery jobs |
| **Multi-tenancy** | Schema-per-org (future) | Start single-tenant; add isolation later |
| **Frontend Style** | Match existing HTML framework | Reuse the excellent Netflix-inspired design system you already have |

---

## 7. Team Composition

**Minimum Viable Team (16 weeks):**
- 1× Full-stack Engineer (React + FastAPI)   — leads architecture
- 1× ML Engineer   — models, feature engineering, confidence scoring
- 1× Frontend Engineer   — UI/UX, dashboards, data viz
- 0.5× DevOps/Platform   — Docker, deployment, infrastructure

**If solo:** Expect 6-8 months. Start with Phase 1 only, add ML later.

---

## 8. Success Metrics (KPIs)

| Metric | Target |
|--------|--------|
| Time to carbon budget (greenlight → prediction) | < 5 minutes |
| Data entry time per daily log | < 10 minutes |
| Invoice extraction accuracy | > 85% |
| Report generation time | < 30 seconds |
| Confidence score coverage | > 90% of line items scored |

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| ML model cold-start (no historical data) | Seed with synthetic data + BAFTA Albert public benchmarks; bootstrap from EPA/DEFRA averages |
| LLM extraction hallucination | Strict Pydantic schema validation + human review queue + citation requirement |
| Emission factor accuracy | Version factors; flag outdated ones; allow overrides |
| User adoption | Start with Green PMs who are already mandated to report; make entry faster than Excel |

---

## 10. Immediate Next Steps

1. **Validate scope:** Confirm which modules are must-have vs. nice-to-have for your first user
2. **Set up repo:** Initialize with the scaffold (I can do this for you)
3. **Seed data:** Gather 3-5 sample productions with real or realistic data
4. **Choose LLM provider:** OpenAI, Anthropic, or Azure OpenAI (enterprise preference?)
5. **Lock deployment target:** Local Docker first, then AWS/GCP/Azure?

---

*This plan distills your 24-month enterprise framework into a 16-week buildable MVP that captures 80% of the value. Every component is designed to scale into the full architecture described in your HTML framework without a rewrite.*
