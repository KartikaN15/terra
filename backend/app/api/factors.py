"""
Emission Factor API
"""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/factors", tags=["Emission Factors"])


@router.post("", response_model=schemas.EmissionFactorOut)
def create_factor(factor: schemas.EmissionFactorCreate, db: Session = Depends(get_db)):
    return crud.create_factor(db, factor)


@router.get("", response_model=List[schemas.EmissionFactorOut])
def list_factors(
    category: Optional[str] = None,
    region: Optional[str] = None,
    subcategory: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_factors(db, category=category, region=region, subcategory=subcategory, search=search, limit=limit)


@router.get("/lookup")
def lookup_factor(
    category: str,
    subcategory: str,
    region: str = "UK",
    standard: Optional[str] = None,
    db: Session = Depends(get_db)
):
    factor = crud.get_best_factor(db, category, subcategory, region, standard)
    if not factor:
        return {"found": False}
    return {"found": True, "factor": schemas.EmissionFactorOut.model_validate(factor)}
