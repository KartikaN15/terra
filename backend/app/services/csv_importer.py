"""CSV bulk importer for activity events."""
import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from .. import crud, schemas
from .calculation_engine import CalculationEngine
from .scope_classifier import classify_scope
from .confidence_scorer import determine_tier, compute_score


REQUIRED_COLUMNS = {
    "production_id",
    "phase",
    "category",
    "subcategory",
    "value",
    "unit",
    "source_type",
    "recorded_at",
    "recorded_by",
}
OPTIONAL_COLUMNS = {"scope", "source_reference", "grid_region", "notes"}
VALID_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


class CSVImportError(Exception):
    pass


def _parse_datetime(value: str) -> Optional[datetime]:
    from datetime import timezone
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def _parse_decimal(value: str) -> Optional[Decimal]:
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def import_events_from_csv(
    db: Session,
    file_content: bytes,
    filename: str = "upload.csv",
    default_region: str = "UK",
) -> Dict[str, Any]:
    """
    Parse a CSV file and create activity events.

    Returns:
        {
            "filename": str,
            "total_rows": int,
            "created": int,
            "errors": [{"row": int, "message": str}],
        }
    """
    calc = CalculationEngine()
    results = {
        "filename": filename,
        "total_rows": 0,
        "created": 0,
        "errors": [],
    }

    try:
        text = file_content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        results["errors"].append({"row": 0, "message": f"Invalid file encoding: {e}"})
        return results

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        results["errors"].append({"row": 0, "message": "CSV has no headers"})
        return results

    headers = set(reader.fieldnames)
    missing_required = REQUIRED_COLUMNS - headers
    if missing_required:
        results["errors"].append({
            "row": 0,
            "message": f"Missing required columns: {', '.join(sorted(missing_required))}",
        })
        return results

    unknown = headers - VALID_COLUMNS
    if unknown:
        results["errors"].append({
            "row": 0,
            "message": f"Unknown columns (ignored): {', '.join(sorted(unknown))}",
        })

    for row_idx, row in enumerate(reader, start=2):  # start=2 because row 1 is header
        results["total_rows"] += 1
        error_prefix = f"Row {row_idx}"

        # Validate production exists
        prod_id = row.get("production_id", "").strip()
        if not prod_id:
            results["errors"].append({"row": row_idx, "message": f"{error_prefix}: production_id is empty"})
            continue
        if not crud.get_production(db, prod_id):
            results["errors"].append({"row": row_idx, "message": f"{error_prefix}: production '{prod_id}' not found"})
            continue

        # Parse value
        value = _parse_decimal(row.get("value", ""))
        if value is None:
            results["errors"].append({"row": row_idx, "message": f"{error_prefix}: invalid numeric value '{row.get('value')}'"})
            continue

        # Parse recorded_at
        recorded_at = _parse_datetime(row.get("recorded_at", ""))
        if recorded_at is None:
            results["errors"].append({"row": row_idx, "message": f"{error_prefix}: invalid datetime '{row.get('recorded_at')}'"})
            continue

        # Grid region
        grid_region = row.get("grid_region", "").strip() or default_region

        # Calculate emissions
        try:
            calc_result = calc.calculate(
                db,
                value,
                row.get("unit", "").strip(),
                row.get("category", "").strip(),
                row.get("subcategory", "").strip(),
                grid_region,
            )
        except ValueError as e:
            results["errors"].append({"row": row_idx, "message": f"{error_prefix}: {e}"})
            continue

        # Scope: factor is authoritative; CSV value is a hint; classifier is last resort.
        scope = (
            calc_result.get("scope")
            or row.get("scope", "").strip()
            or classify_scope(row.get("subcategory", "").strip())
        )

        # Confidence scoring
        factor = crud.get_factor(db, calc_result.get("factor_id")) if calc_result.get("factor_id") else None
        tier = determine_tier(row.get("source_type", ""), row.get("source_reference") or "")
        confidence = compute_score(tier, factor, row.get("source_reference") or "", calc_result=calc_result)

        # Create event
        event_create = schemas.ActivityEventCreate(
            production_id=prod_id,
            phase=row.get("phase", "").strip(),
            scope=scope,
            category=row.get("category", "").strip(),
            subcategory=row.get("subcategory", "").strip(),
            value=value,
            unit=row.get("unit", "").strip(),
            source_type=row.get("source_type", "").strip(),
            source_reference=row.get("source_reference") or None,
            grid_region=grid_region if grid_region != default_region else None,
            recorded_at=recorded_at,
            recorded_by=row.get("recorded_by", "").strip(),
            notes=row.get("notes") or None,
        )

        try:
            crud.create_event(
                db,
                event_create,
                kgco2e=calc_result["kgco2e"],
                confidence_tier=tier,
                confidence_score=confidence,
                emission_factor_id=calc_result.get("factor_id"),
                emission_factor_version=calc_result["factor_version"],
                calculation_method=calc_result["calculation_method"],
                gwp_version=calc_result.get("gwp_version"),
                region_match=calc_result.get("region_match"),
                unit_converted=calc_result.get("unit_converted", False),
            )
            results["created"] += 1
        except Exception as e:
            results["errors"].append({"row": row_idx, "message": f"{error_prefix}: database error: {e}"})

    return results
