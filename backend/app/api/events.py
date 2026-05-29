"""
Activity Event API
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user_optional
from ..services.calculation_engine import CalculationEngine
from ..services.scope_classifier import classify_scope
from ..services.confidence_scorer import determine_tier, compute_score
from ..services.csv_importer import import_events_from_csv

calc = CalculationEngine()

router = APIRouter(prefix="/events", tags=["Activity Events"])


@router.post("", response_model=schemas.ActivityEventOut)
def create_event(event: schemas.ActivityEventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_optional)):
    if current_user:
        event = event.model_copy(update={"recorded_by": current_user.user_id})

    # Lookup emission factor and calculate
    try:
        result = calc.calculate(
            db, event.value, event.unit, event.category, event.subcategory,
            event.grid_region or "UK"
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Scope: factor is authoritative when present; user input is a hint;
    # keyword classifier is the last-resort fallback.
    scope = result.get("scope") or event.scope or classify_scope(event.subcategory)
    event = event.model_copy(update={"scope": scope})

    # Confidence scoring   — reuse the factor already loaded by the resolver
    # to avoid a second DB round-trip.
    factor = result.get("factor")
    tier = determine_tier(event.source_type, event.source_reference or "")
    confidence = compute_score(tier, factor, event.source_reference or "", calc_result=result)

    return crud.create_event(
        db, event,
        kgco2e=result["kgco2e"],
        confidence_tier=tier,
        confidence_score=confidence,
        emission_factor_id=result.get("factor_id"),
        emission_factor_version=result["factor_version"],
        calculation_method=result["calculation_method"],
        gwp_version=result.get("gwp_version"),
        region_match=result.get("region_match"),
        unit_converted=result.get("unit_converted", False),
    )


@router.get("/production/{production_id}", response_model=List[schemas.ActivityEventOut])
def list_events(production_id: str, skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    return crud.get_events_by_production(db, production_id, skip=skip, limit=limit)


@router.get("/{event_id}", response_model=schemas.ActivityEventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@router.patch("/{event_id}", response_model=schemas.ActivityEventOut)
def patch_event(event_id: str, updates: schemas.ActivityEventUpdate, db: Session = Depends(get_db)):
    """Update an event's editable fields. Note: does NOT recalculate kgco2e;
    use /recalculate to refresh the emission calculation after editing."""
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    allowed = {"phase", "scope", "category", "subcategory", "value", "unit",
                "source_type", "source_reference", "grid_region", "notes", "recorded_at"}
    payload = updates.model_dump(exclude_unset=True)
    updates_dict = {k: v for k, v in payload.items() if k in allowed}
    updated = crud.update_event(db, event_id, updates_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated


@router.delete("/{event_id}")
def delete_event(event_id: str, db: Session = Depends(get_db)):
    if not crud.delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"deleted": True}


@router.post("/{event_id}/recalculate", response_model=schemas.ActivityEventOut)
def recalculate_event(event_id: str, db: Session = Depends(get_db)):
    """Re-resolve the best emission factor for an existing event and refresh
    its kgco2e, audit signals, and confidence. Useful after the factor library
    is updated (new vintage, new region row, retired factor)."""
    db_event = crud.get_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        result = calc.calculate(
            db, db_event.value, db_event.unit, db_event.category, db_event.subcategory,
            db_event.grid_region or "UK",
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    factor = result.get("factor")
    tier = determine_tier(db_event.source_type, db_event.source_reference or "")
    confidence = compute_score(tier, factor, db_event.source_reference or "", calc_result=result)

    db_event.kgco2e = result["kgco2e"]
    db_event.kgco2e_wtt = result.get("kgco2e_wtt")
    db_event.confidence_tier = tier
    db_event.confidence_score = confidence
    db_event.emission_factor_id = result["factor_id"]
    db_event.emission_factor_version = result["factor_version"]
    db_event.calculation_method = result["calculation_method"]
    db_event.gwp_version = result.get("gwp_version")
    db_event.region_match = result.get("region_match")
    db_event.unit_converted = bool(result.get("unit_converted", False))
    db_event.scope = result.get("scope") or db_event.scope
    db.commit()
    db.refresh(db_event)
    return db_event


@router.post("/bulk-upload", response_model=schemas.BulkEventResult)
def bulk_upload_events(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a CSV file of activity events for bulk import."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = file.file.read()
    result = import_events_from_csv(db, content, filename=file.filename)

    if result["total_rows"] == 0 and result["errors"]:
        # Hard failure if we couldn't even start
        raise HTTPException(status_code=422, detail=result["errors"])

    return result
