"""
ML API Endpoints
Wires ml_engine models into FastAPI.
"""
import threading
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db, SessionLocal
from .. import schemas, models, crud

_router_lock = threading.Lock()

router = APIRouter(prefix="/ml", tags=["ML"])

# Lazy-initialized pipeline
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    with _router_lock:
        if _pipeline is not None:
            return _pipeline
        from ml_engine.pipeline import MLPipeline
        import os
        _pipeline = MLPipeline.for_domain("film_tv", model_dir=os.environ.get("MODEL_DIR", "./models"))
        # Try auto-load latest greenlight model
        try:
            latest = _pipeline.get_latest_version()
            if latest:
                _pipeline.greenlight.load(latest)
                print(f"[MLPipeline] Auto-loaded greenlight model: {latest}")
        except Exception as e:
            print(f"[MLPipeline] Could not auto-load: {e}")
    return _pipeline


def _train_if_needed(pipeline, db: Session, kind: str = "greenlight"):
    """Trigger training if no model is loaded."""
    if kind == "greenlight" and pipeline.greenlight.model:
        return
    # Load projects from DB
    prods = crud.get_productions(db)
    projects = []
    for p in prods:
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
    if len(projects) < 5:
        return
    pipeline.train_all(projects)


@router.post("/forecast/greenlight", response_model=schemas.GreenlightForecastResponse)
def forecast_greenlight(req: schemas.GreenlightForecastRequest, db: Session = Depends(get_db)):
    pipeline = _get_pipeline()
    if not pipeline.greenlight.model:
        _train_if_needed(pipeline, db, kind="greenlight")
    if not pipeline.greenlight.model:
        raise HTTPException(status_code=503, detail="Greenlight model not available. Train models first.")
    from ml_engine.schemas import ProjectMetadata, GreenlightPredictRequest
    request = GreenlightPredictRequest(
        project_id=req.project_id,
        metadata=ProjectMetadata(**req.metadata.model_dump()),
    )
    result = pipeline.predict_greenlight(request)
    return schemas.GreenlightForecastResponse(
        project_id=result.project_id,
        predicted_total_tco2e=result.predicted_total_tco2e,
        interval_lower_tco2e=result.interval_lower_tco2e,
        interval_upper_tco2e=result.interval_upper_tco2e,
        confidence=result.confidence,
        top_driver=result.shap_attribution[0].feature if result.shap_attribution else "",
        model_version=result.model_version,
    )


@router.post("/train")
def train_models(background_tasks: BackgroundTasks, kinds: Optional[List[str]] = None, db: Session = Depends(get_db)):
    pipeline = _get_pipeline()
    targets = kinds or ["greenlight", "imputer"]

    def _do_train():
        _train_if_needed(pipeline, SessionLocal(), kind="greenlight")

    background_tasks.add_task(_do_train)
    return {"status": "training_started", "kinds": targets}


@router.get("/health")
def ml_health():
    pipeline = _get_pipeline()
    return {
        "greenlight_loaded": pipeline.greenlight.model is not None,
        "greenlight_version": pipeline.get_latest_version(),
        "imputer_loaded": pipeline.imputer.model is not None if hasattr(pipeline, "imputer") else False,
        "training_in_progress": False,
        "last_trained_at": None,
        "last_error": None,
    }


@router.post("/anomalies/detect")
def detect_anomalies(req: schemas.AnomalyDetectRequestAPI):
    pipeline = _get_pipeline()
    from ml_engine.schemas import TimeSeriesPoint, AnomalyDetectRequest
    ts = [TimeSeriesPoint(timestamp=datetime.fromisoformat(str(p["timestamp"])), kgco2e=p["kgco2e"]) for p in req.time_series]
    anom_req = AnomalyDetectRequest(project_id=req.project_id, time_series=ts, window_days=req.window_days, sensitivity=req.sensitivity)
    result = pipeline.detect_anomalies(anom_req)
    return {
        "project_id": result.project_id,
        "anomalies": [
            {
                "timestamp": a.timestamp.isoformat(),
                "observed_kgco2e": float(a.observed_kgco2e),
                "expected_kgco2e": float(a.expected_kgco2e),
                "deviation_percent": float(a.deviation_percent),
                "severity": a.severity.value,
                "reason": getattr(a, "reason", ""),
                "z_score": getattr(a, "z_score", None),
            }
            for a in result.anomalies
        ],
        "window_days": result.window_days,
    }
