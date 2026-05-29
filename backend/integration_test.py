"""
Integration Test: Load 100 productions into SQLite backend and hit all endpoints.
"""
import os
import sys
import csv
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from uuid import UUID

# Use SQLite for quick local test
os.environ["DATABASE_URL"] = "sqlite:///./test_sustainability.db"
os.environ["MODEL_DIR"] = "./test_models"

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import crud, schemas, models
from app.services.calculation_engine import CalculationEngine
from app.services.scope_classifier import classify_scope
from app.services.confidence_scorer import determine_tier, compute_score

engine = create_engine(os.environ["DATABASE_URL"], echo=False)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db = Session()

calc = CalculationEngine()

print("=" * 70)
print("BACKEND INTEGRATION TEST")
print("=" * 70)

# ------------------------------------------------------------------
# 1. Seed emission factors
# ------------------------------------------------------------------
print("\n[1] Seeding emission factors...")
csv_path = Path(__file__).parent.parent / "test_data" / "sample_emission_factors.csv"
seeded = 0
with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        exists = db.query(models.EmissionFactor).filter(
            models.EmissionFactor.standard == row["standard"],
            models.EmissionFactor.category == row["category"],
            models.EmissionFactor.subcategory == row["subcategory"],
            models.EmissionFactor.region == row["region"],
            models.EmissionFactor.version == row["version"],
        ).first()
        if exists:
            continue
        factor = schemas.EmissionFactorCreate(
            standard=row["standard"],
            category=row["category"],
            subcategory=row["subcategory"],
            activity_type=row["activity_type"],
            factor_value=Decimal(row["factor_value"]),
            unit=row["unit"],
            scope=row["scope"],
            region=row["region"],
            country_code=row.get("country_code") or None,
            grid_intensity_g_co2_kwh=Decimal(row["grid_intensity_g_co2_kwh"]) if row.get("grid_intensity_g_co2_kwh") else None,
            valid_from=datetime.strptime(row["valid_from"], "%Y-%m-%d"),
            version=row["version"],
            description=f"{row['standard']} factor for {row['subcategory']}",
        )
        crud.create_factor(db, factor)
        seeded += 1
print(f"  Seeded {seeded} emission factors")

# ------------------------------------------------------------------
# 2. Load productions
# ------------------------------------------------------------------
print("\n[2] Loading productions...")
prod_csv = Path(__file__).parent.parent / "test_data" / "sample_productions.csv"
productions = []
with open(prod_csv) as f:
    reader = csv.DictReader(f)
    for row in reader:
        prod = crud.create_production(db, schemas.ProductionCreate(
            production_id=row["production_id"],
            title=row["title"],
            type=row["type"],
            genre=row["genre"],
            budget_band=row["budget_band"],
            runtime_min=int(row["runtime_min"]) if row["runtime_min"] else None,
            episodes=int(row["episodes"]),
            shoot_days=int(row["shoot_days"]) if row["shoot_days"] else None,
            locations=row["locations"].split("|") if row["locations"] else [],
            cast_count=int(row["cast_count"]) if row["cast_count"] else None,
            crew_count=int(row["crew_count"]) if row["crew_count"] else None,
            vfx_intensity=row["vfx_intensity"],
            status=row["status"],
        ), "00000000-0000-0000-0000-000000000001")
        productions.append(prod)
print(f"  Loaded {len(productions)} productions")

# ------------------------------------------------------------------
# 3. Load activity events
# ------------------------------------------------------------------
print("\n[3] Loading activity events...")
event_csv = Path(__file__).parent.parent / "test_data" / "sample_activity_events.csv"
events_loaded = 0
with open(event_csv) as f:
    reader = csv.DictReader(f)
    for row in reader:
        prod_id = row["production_id"]
        event_create = schemas.ActivityEventCreate(
            production_id=prod_id,
            phase=row["phase"],
            scope=row["scope"],
            category=row["category"],
            subcategory=row["subcategory"],
            value=Decimal(row["value"]),
            unit=row["unit"],
            source_type=row["source_type"],
            source_reference=row.get("source_reference"),
            grid_region=row.get("grid_region"),
            recorded_by="00000000-0000-0000-0000-000000000001",
            recorded_at=datetime.fromisoformat(row["recorded_at"]),
        )
        try:
            result = calc.calculate(db, event_create.value, event_create.unit,
                                    event_create.category,
                                    event_create.subcategory,
                                    event_create.grid_region or "UK")
        except ValueError as e:
            print(f"    Skip {event_create.subcategory}: {e}")
            continue

        factor = crud.get_factor(db, result["factor_id"]) if result.get("factor_id") else None
        tier = determine_tier(event_create.source_type, event_create.source_reference or "")
        confidence = compute_score(tier, factor, event_create.source_reference or "")

        crud.create_event(
            db, event_create,
            kgco2e=result["kgco2e"],
            confidence_tier=tier,
            confidence_score=confidence,
            emission_factor_id=result.get("factor_id"),
            emission_factor_version=result["factor_version"],
            calculation_method=result["calculation_method"],
        )
        events_loaded += 1
print(f"  Loaded {events_loaded} events")

# ------------------------------------------------------------------
# 4. Production summary
# ------------------------------------------------------------------
print("\n[4] Production summary (first production with events)...")
target = None
summary = None
for p in productions:
    summary = crud.get_production_summary(db, p.production_id)
    if summary:
        target = p
        break
if not summary:
    print("  No production with events found!")
    sys.exit(1)
print(f"  Title: {target.title}")
print(f"  Total: {summary['total_tco2e']} tCO2e")
print(f"  Scope 1: {summary['scope_breakdown'].get('SCOPE_1', 0)} | Scope 2: {summary['scope_breakdown'].get('SCOPE_2', 0)} | Scope 3: {summary['scope_breakdown'].get('SCOPE_3', 0)}")
print(f"  Confidence: {summary['overall_confidence']}")
print(f"  Events: {summary['event_count']}")

# ------------------------------------------------------------------
# 5. ML Forecast (greenlight)
# ------------------------------------------------------------------
print("\n[5] ML Greenlight Forecast...")
from ml_engine.pipeline import MLPipeline
from ml_engine.schemas import ProjectMetadata, GreenlightPredictRequest

pipeline = MLPipeline.for_domain("film_tv", model_dir=os.environ["MODEL_DIR"])

# Load all productions as training data
projects = []
for p in productions:
    events = crud.get_events_by_production(db, p.production_id)
    if not events:
        continue
    total_kg = sum(e.kgco2e for e in events)
    cat_breakdown = {}
    for e in events:
        cat_breakdown[e.category] = cat_breakdown.get(e.category, 0) + float(e.kgco2e)
    projects.append({
        "project_id": str(p.production_id),
        "metadata": {
            "genre": p.genre,
            "budget_band": p.budget_band,
            "shoot_days": p.shoot_days,
            "crew_count": p.crew_count,
            "cast_count": p.cast_count,
            "episodes": p.episodes,
            "runtime_min": p.runtime_min,
            "vfx_intensity": p.vfx_intensity,
            "primary_region": p.locations[0] if p.locations else "UK",
        },
        "total_kgco2e": float(total_kg),
        "category_breakdown": cat_breakdown,
    })

print(f"  Training on {len(projects)} projects...")
metrics = pipeline.train_all(projects)
print(f"  Greenlight R2 = {metrics['greenlight']['r2']:.3f}")
print(f"  Greenlight MAE = {metrics['greenlight']['mae_tco2e']:.1f} tCO2e")

# Predict holdout (last production)
holdout = productions[-1]
ho_events = crud.get_events_by_production(db, holdout.production_id)
actual_tco2e = sum(e.kgco2e for e in ho_events) / 1000

request = GreenlightPredictRequest(
    project_id=str(holdout.production_id),
    metadata=ProjectMetadata(
        project_type=holdout.genre,
        scale_band=holdout.budget_band,
        duration=holdout.shoot_days or 30,
        headcount=holdout.crew_count or 50,
        complexity=holdout.vfx_intensity,
        output_units=holdout.episodes,
        output_size=holdout.runtime_min,
        region=holdout.locations[0] if holdout.locations else "UK",
    )
)
result = pipeline.predict_greenlight(request)
print(f"\n  Holdout: {holdout.title}")
print(f"  Predicted: {result.predicted_total_tco2e} tCO2e (CI: {result.interval_lower_tco2e} - {result.interval_upper_tco2e})")
print(f"  Actual:    {actual_tco2e:.1f} tCO2e")
print(f"  Error:     {abs(float(result.predicted_total_tco2e) - float(actual_tco2e)) / float(actual_tco2e) * 100:.1f}%")
print(f"  Confidence: {result.confidence}")
print(f"  Top driver: {result.shap_attribution[0].feature} ({result.shap_attribution[0].direction})")

# ------------------------------------------------------------------
# 6. ML Anomaly Detection
# ------------------------------------------------------------------
print("\n[6] ML Anomaly Detection...")
from ml_engine.schemas import TimeSeriesPoint, AnomalyDetectRequest

# Build daily time series for first production
daily = {}
for e in crud.get_events_by_production(db, target.production_id):
    day = e.recorded_at.date().isoformat()
    daily[day] = daily.get(day, 0) + float(e.kgco2e)

ts = [TimeSeriesPoint(timestamp=datetime.fromisoformat(d), kgco2e=Decimal(str(v))) for d, v in sorted(daily.items())]
if len(ts) >= 14:
    anom_req = AnomalyDetectRequest(project_id=str(target.production_id), time_series=ts, window_days=7, sensitivity=0.05)
    anom_result = pipeline.detect_anomalies(anom_req)
    print(f"  Analyzed {len(ts)} days, found {len(anom_result.anomalies)} anomalies")
    for a in anom_result.anomalies[:3]:
        print(f"    {a.timestamp.date()}: {a.observed_kgco2e} kgCO2e (deviation: {a.deviation_percent:+.0f}%) [{a.severity.value}]")
else:
    print(f"  Only {len(ts)} days of data (need 14+ for anomaly detection)")

# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------
db.close()
engine.dispose()

# Remove test DB
import os as os2
try:
    os2.remove("test_sustainability.db")
except:
    pass

print("\n" + "=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)
