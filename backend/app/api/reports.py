"""
Reporting & Export API
Albert-compatible CSV, PDF, and disclosure templates.
"""
import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/albert-export/{production_id}")
def export_albert_csv(production_id: str, db: Session = Depends(get_db)):
    """
    Export a BAFTA Albert-compatible CSV for a production.
    Columns: Date, Category, Subcategory, Activity, Quantity, Unit, kgCO2e, Scope, DataQuality
    """
    prod = crud.get_production(db, production_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Production not found")

    events = crud.get_events_by_production(db, production_id)
    if not events:
        raise HTTPException(status_code=404, detail="No events found for production")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ProductionName", "Date", "Category", "Subcategory", "Activity",
        "Quantity", "Unit", "kgCO2e", "Scope", "DataQuality", "SourceReference"
    ])

    for e in events:
        writer.writerow([
            prod.title,
            e.recorded_at.strftime("%Y-%m-%d") if e.recorded_at else "",
            e.category,
            e.subcategory,
            e.subcategory.replace("_", " ").title(),
            str(e.value),
            e.unit,
            str(e.kgco2e),
            e.scope,
            e.confidence_tier.replace("TIER_1_", "Tier 1 - ").replace("TIER_2_", "Tier 2 - ").replace("TIER_3_", "Tier 3 - "),
            e.source_reference or "",
        ])

    output.seek(0)
    filename = f"{prod.title.replace(' ', '_')}_Albert_Export.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
