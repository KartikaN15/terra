"""
Production CRUD + Summary API
"""

from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user_optional
from ..services.calculation_engine import CalculationEngine
from ..services.confidence_scorer import determine_tier, compute_score
from ..services.oed_playbook import generate_recommendations

_calc = CalculationEngine()

router = APIRouter(prefix="/productions", tags=["Productions"])


@router.post("", response_model=schemas.ProductionOut)
def create_production(prod: schemas.ProductionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_optional)):
    created_by = current_user.user_id if current_user else "00000000-0000-0000-0000-000000000001"
    db_prod = crud.create_production(db, prod, created_by)
    crud.create_notification(
        db,
        user_id=created_by,
        type="SYSTEM",
        title="Production created",
        message=f"'{db_prod.title}' has been created. Start adding activity events to track its carbon footprint.",
        entity_type="production",
        entity_id=db_prod.production_id,
    )
    return db_prod


@router.get("", response_model=List[schemas.ProductionOut])
def list_productions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_productions(db, skip=skip, limit=limit)


@router.get("/{production_id}", response_model=schemas.ProductionOut)
def get_production(production_id: str, db: Session = Depends(get_db)):
    db_prod = crud.get_production(db, production_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Production not found")
    return db_prod


@router.get("/{production_id}/summary")
def get_summary(production_id: str, db: Session = Depends(get_db)):
    summary = crud.get_production_summary(db, production_id)
    if not summary:
        raise HTTPException(status_code=404, detail="No events found for production")
    return summary


@router.patch("/{production_id}", response_model=schemas.ProductionOut)
def update_production(production_id: str, updates: schemas.ProductionUpdate, db: Session = Depends(get_db)):
    db_prod = crud.update_production(db, production_id, updates)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Production not found")
    return db_prod


@router.delete("/{production_id}")
def delete_production(production_id: str, db: Session = Depends(get_db)):
    if not crud.delete_production(db, production_id):
        raise HTTPException(status_code=404, detail="Production not found")
    return {"deleted": True}


@router.get("/{production_id}/recommendations")
def get_recommendations(production_id: str, db: Session = Depends(get_db)):
    summary = crud.get_production_summary(db, production_id)
    if not summary:
        raise HTTPException(status_code=404, detail="No events found for production")
    prod = crud.get_production(db, production_id)
    meta = {
        "vfx_intensity": prod.vfx_intensity if prod else None,
        "budget_band": prod.budget_band if prod else None,
    }
    recs = generate_recommendations(
        category_breakdown={k: Decimal(str(v)) for k, v in summary.get("category_breakdown", {}).items()},
        total_tco2e=Decimal(str(summary.get("total_tco2e", 0))),
        production_meta=meta,
    )
    return {
        "production_id": production_id,
        "recommendations": [
            {
                "id": r.id,
                "category": r.category,
                "action": r.action,
                "description": r.description,
                "estimated_saving_tco2e": float(r.estimated_saving_tco2e),
                "estimated_cost_gbp": float(r.estimated_cost_gbp) if r.estimated_cost_gbp is not None else None,
                "effort": r.effort,
                "impact": r.impact,
                "playbook": r.playbook,
            }
            for r in recs
        ],
        "total_potential_saving_tco2e": float(sum(r.estimated_saving_tco2e for r in recs)),
    }


@router.get("/{production_id}/planner")
def get_planner(production_id: str, db: Session = Depends(get_db)):
    """Get the saved visual planner state for a production."""
    db_prod = crud.get_production(db, production_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Production not found")
    return {
        "production_id": production_id,
        "planner_state": db_prod.planner_state,
    }


@router.post("/{production_id}/planner")
def save_planner(production_id: str, payload: dict, db: Session = Depends(get_db)):
    """Save the visual planner state for a production.

    Body: {"nodes": [...], "edges": [...], "lastDayId": "..."}
    """
    db_prod = crud.get_production(db, production_id)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Production not found")
    db_prod.planner_state = payload
    db.commit()
    db.refresh(db_prod)
    return {
        "production_id": production_id,
        "saved": True,
        "node_count": len(payload.get("nodes", [])),
        "edge_count": len(payload.get("edges", [])),
    }


@router.post("/{production_id}/recalculate-all")
def recalculate_all_events(production_id: str, db: Session = Depends(get_db)):
    """Re-run factor resolution for every event on this production.

    Run after an emission-factor library refresh so historical events pick up
    the new vintage / regional row. Returns a summary of what changed; rows
    that fail resolution are reported but do not abort the batch.
    """
    if not crud.get_production(db, production_id):
        raise HTTPException(status_code=404, detail="Production not found")

    events = crud.get_events_by_production(db, production_id)
    updated, unchanged, failed = 0, 0, []
    delta_kg = Decimal("0")

    for ev in events:
        try:
            result = _calc.calculate(
                db, ev.value, ev.unit, ev.category, ev.subcategory,
                ev.grid_region or "UK",
            )
        except ValueError as e:
            failed.append({"event_id": ev.event_id, "error": str(e)})
            continue

        new_kg = result["kgco2e"]
        new_factor_id = result["factor_id"]
        if (
            ev.kgco2e == new_kg
            and ev.emission_factor_id == new_factor_id
            and ev.emission_factor_version == result["factor_version"]
        ):
            unchanged += 1
            continue

        delta_kg += (Decimal(str(new_kg)) - (ev.kgco2e or Decimal("0")))
        factor = result.get("factor")
        tier = determine_tier(ev.source_type, ev.source_reference or "")
        confidence = compute_score(tier, factor, ev.source_reference or "", calc_result=result)

        ev.kgco2e = new_kg
        ev.kgco2e_wtt = result.get("kgco2e_wtt")
        ev.confidence_tier = tier
        ev.confidence_score = confidence
        ev.emission_factor_id = new_factor_id
        ev.emission_factor_version = result["factor_version"]
        ev.calculation_method = result["calculation_method"]
        ev.gwp_version = result.get("gwp_version")
        ev.region_match = result.get("region_match")
        ev.unit_converted = bool(result.get("unit_converted", False))
        ev.scope = result.get("scope") or ev.scope
        updated += 1

    db.commit()
    return {
        "production_id": production_id,
        "events_total": len(events),
        "events_updated": updated,
        "events_unchanged": unchanged,
        "events_failed": failed,
        "delta_tco2e": float(round(delta_kg / Decimal("1000"), 4)),
    }
