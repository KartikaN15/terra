"""
Document Upload, OCR/Extraction, and Review API
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user_optional
from ..services.document_extractor import extract_document
from ..services.calculation_engine import CalculationEngine
from ..services.scope_classifier import classify_scope
from ..services.confidence_scorer import determine_tier, compute_score

router = APIRouter(prefix="/documents", tags=["Documents"])

# Local upload directory (MVP: filesystem; prod: swap to S3/MinIO)
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

calc = CalculationEngine()


@router.post("/upload", response_model=schemas.DocumentOut)
def upload_document(
    production_id: str,
    doc_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional),
):
    """Upload a document and create a Document record."""
    prod = crud.get_production(db, production_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Production not found")

    # Validate doc_type
    valid_types = {"FUEL_RECEIPT", "ELECTRICITY_BILL", "TRAVEL_MANIFEST",
                   "CATERING_INVOICE", "WASTE_TICKET", "HOTEL_INVOICE", "EPD", "OTHER"}
    if doc_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid doc_type. Valid: {valid_types}")

    # Save file locally
    doc_id = str(uuid.uuid4())
    prod_dir = UPLOAD_DIR / production_id
    prod_dir.mkdir(exist_ok=True)
    safe_filename = file.filename or "unnamed"
    dest_path = prod_dir / f"{doc_id}_{safe_filename}"

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB record
    db_doc = models.Document(
        doc_id=doc_id,
        production_id=production_id,
        doc_type=doc_type,
        s3_path=str(dest_path),
        filename=safe_filename,
        file_size_bytes=dest_path.stat().st_size,
        mime_type=file.content_type or "application/octet-stream",
        ocr_status="PENDING",
        review_status="PENDING",
        uploaded_by=current_user.user_id if current_user else "00000000-0000-0000-0000-000000000001",
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


@router.get("/production/{production_id}", response_model=List[schemas.DocumentOut])
def list_documents(production_id: str, db: Session = Depends(get_db)):
    """List all documents for a production."""
    docs = db.query(models.Document).filter(
        models.Document.production_id == production_id
    ).order_by(models.Document.uploaded_at.desc()).all()
    return docs


@router.get("/{doc_id}", response_model=schemas.DocumentOut)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{doc_id}/extract")
def extract_document_endpoint(doc_id: str, db: Session = Depends(get_db)):
    """Run extraction pipeline on a document."""
    doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Read file content as raw text (MVP: read text files directly; binary files get placeholder)
    file_path = Path(doc.s3_path)
    raw_text = ""
    try:
        if doc.mime_type and doc.mime_type == "application/pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif doc.mime_type and doc.mime_type.startswith("text/"):
            raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
        else:
            # For MVP, attempt to read as text anyway (many PDFs/invoices are text-extractable)
            raw_text = file_path.read_text(encoding="utf-8", errors="ignore")[:20000]
    except Exception:
        raw_text = ""

    # Run extraction
    result = extract_document(doc.doc_type, raw_text or doc.filename, doc.filename)

    doc.ocr_status = "EXTRACTED" if result["items"] else "REVIEW_REQUIRED"
    doc.extracted_raw_text = raw_text[:5000]  # Store truncated
    doc.extracted_data = result
    doc.extracted_confidence = result["confidence"]
    doc.extracted_by_model = result["model"]

    # If confidence is low, flag for review
    if result["confidence"] < 0.70:
        doc.review_status = "PENDING"
    else:
        doc.review_status = "PENDING"  # Still requires human approval for MVP

    db.commit()
    db.refresh(doc)

    # Notify user
    item_count = len(doc.extracted_data.get("items", [])) if doc.extracted_data else 0
    crud.create_notification(
        db,
        user_id=doc.uploaded_by,
        type="DOCUMENT_EXTRACTED",
        title=f"Document extraction complete",
        message=f"'{doc.filename}' extracted with {doc.extracted_confidence:.0%} confidence. {item_count} item(s) found.",
        entity_type="document",
        entity_id=doc.doc_id,
    )

    return {
        "doc_id": doc.doc_id,
        "ocr_status": doc.ocr_status,
        "extracted_data": doc.extracted_data,
        "extracted_confidence": doc.extracted_confidence,
        "review_status": doc.review_status,
    }


@router.post("/{doc_id}/approve")
def approve_document(doc_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_optional)):
    """Approve extracted data and create ActivityEvents."""
    doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.extracted_data or not doc.extracted_data.get("items"):
        raise HTTPException(status_code=422, detail="No extracted data to approve")

    created_event_ids = []
    for item in doc.extracted_data["items"]:
        value = Decimal(str(item["value"]))
        category = item["category"]
        subcategory = item["subcategory"]
        region = item.get("grid_region") or "UK"

        # Calculate emissions
        try:
            calc_result = calc.calculate(
                db, value, item["unit"], category, subcategory, region
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Calculation failed for {subcategory}: {e}")

        factor = crud.get_factor(db, calc_result.get("factor_id")) if calc_result.get("factor_id") else None
        tier = determine_tier("INVOICE_OCR", doc.filename)
        confidence = compute_score(tier, factor, doc.filename)

        recorded_at = item.get("recorded_at")
        if recorded_at:
            from datetime import datetime, timezone
            try:
                recorded_at = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
            except Exception:
                recorded_at = datetime.now(timezone.utc)
        else:
            from datetime import datetime, timezone
            recorded_at = datetime.now(timezone.utc)

        event_create = schemas.ActivityEventCreate(
            production_id=doc.production_id,
            phase=item.get("phase", "PRODUCTION"),
            scope=classify_scope(subcategory),
            category=category,
            subcategory=subcategory,
            value=value,
            unit=item["unit"],
            source_type="INVOICE_OCR",
            source_reference=doc.filename,
            grid_region=region,
            recorded_at=recorded_at,
            recorded_by=current_user.user_id if current_user else "00000000-0000-0000-0000-000000000001",
            notes=item.get("notes", ""),
        )

        db_event = crud.create_event(
            db, event_create,
            kgco2e=calc_result["kgco2e"],
            confidence_tier=tier,
            confidence_score=confidence,
            emission_factor_id=calc_result.get("factor_id"),
            emission_factor_version=calc_result["factor_version"],
            calculation_method=calc_result["calculation_method"],
        )
        created_event_ids.append(db_event.event_id)

    doc.review_status = "APPROVED"
    doc.linked_event_ids = created_event_ids
    db.commit()
    db.refresh(doc)

    return {
        "approved": True,
        "created_events": len(created_event_ids),
        "event_ids": created_event_ids,
    }


@router.post("/{doc_id}/reject")
def reject_document(doc_id: str, db: Session = Depends(get_db)):
    """Reject extracted data."""
    doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.review_status = "REJECTED"
    db.commit()
    return {"rejected": True}


@router.get("/pending-review")
def pending_review(db: Session = Depends(get_db)):
    """Get all documents awaiting human review."""
    docs = db.query(models.Document).filter(
        models.Document.review_status == "PENDING",
        models.Document.ocr_status.in_(["EXTRACTED", "REVIEW_REQUIRED"]),
    ).order_by(models.Document.uploaded_at.desc()).all()
    return docs
