"""
Document Extractor   — Heuristic-based extraction for production sustainability docs.
MVP approach: rule-based parsing per doc_type, no external LLM/OCR required.
In production, swap this for Tesseract + LiteLLM pipeline.
"""
import re
import random
from decimal import Decimal
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Tuple

from .llm_extractor import extract_with_llm


class ExtractedItem:
    def __init__(
        self,
        category: str,
        subcategory: str,
        value: Decimal,
        unit: str,
        phase: str = "PRODUCTION",
        grid_region: Optional[str] = None,
        recorded_at: Optional[datetime] = None,
        notes: str = "",
    ):
        self.category = category
        self.subcategory = subcategory
        self.value = value
        self.unit = unit
        self.phase = phase
        self.grid_region = grid_region
        self.recorded_at = recorded_at or datetime.now(timezone.utc)
        self.notes = notes


def _extract_numbers(text: str) -> List[Decimal]:
    """Find all decimal numbers in text."""
    found = re.findall(r"\d{1,8}(?:[.,]\d{1,4})?", text)
    results = []
    for f in found:
        try:
            results.append(Decimal(f.replace(",", ".")))
        except:
            pass
    return results


def _guess_date(text: str) -> Optional[datetime]:
    """Try to find a date in common formats."""
    patterns = [
        (r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", lambda m: _parse_date_match(m, dmy=True)),
        (r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", lambda m: _parse_date_match(m, ymd=True)),
    ]
    for pat, parser in patterns:
        m = re.search(pat, text)
        if m:
            dt = parser(m)
            if dt:
                return dt
    return None


def _parse_date_match(m, dmy=False, ymd=False) -> Optional[datetime]:
    try:
        if ymd:
            y, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return datetime(y, a, b, tzinfo=timezone.utc)
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000
        # Simple heuristic: if a > 12, it's likely day-first
        if a > 12:
            return datetime(y, b, a, tzinfo=timezone.utc)
        return datetime(y, a, b, tzinfo=timezone.utc)
    except Exception:
        return None


def _fuel_receipt_extract(text: str, filename: str) -> Tuple[List[ExtractedItem], float]:
    """Extract fuel data from receipt text."""
    text_lower = text.lower()
    nums = _extract_numbers(text)

    # Detect fuel type
    subcategory = "diesel_generator"
    if "hvo" in text_lower or "vegetable" in text_lower:
        subcategory = "hvo_fuel"
    elif "petrol" in text_lower or "gasoline" in text_lower:
        subcategory = "petrol_vehicle"
    elif "lpg" in text_lower:
        subcategory = "lpg"
    elif "kerosene" in text_lower:
        subcategory = "kerosene"

    # Find litres/gallons
    value = None
    unit = "LITRES"
    for n in nums:
        if 10 <= n <= 50000:  # plausible fuel volume
            value = n
            break

    if value is None and nums:
        value = nums[0]

    confidence = 0.75 if value else 0.45
    if "total" in text_lower or "litre" in text_lower or "gal" in text_lower:
        confidence = min(0.92, confidence + 0.10)

    dt = _guess_date(text)
    items = []
    if value:
        items.append(ExtractedItem(
            category="ENERGY",
            subcategory=subcategory,
            value=value,
            unit=unit,
            phase="PRODUCTION",
            recorded_at=dt,
            notes=f"Extracted from {filename}",
        ))
    return items, confidence


def _electricity_bill_extract(text: str, filename: str) -> Tuple[List[ExtractedItem], float]:
    """Extract kWh from electricity bill."""
    text_lower = text.lower()
    nums = _extract_numbers(text)

    # Find kWh value (usually the largest plausible number)
    value = None
    for n in sorted(nums, reverse=True):
        if 50 <= n <= 1000000:  # plausible kWh range
            value = n
            break

    # Detect region
    region = "UK"
    if "california" in text_lower or "pge" in text_lower or "cal" in text_lower:
        region = "US"
    elif "germany" in text_lower or "euro" in text_lower or "eur" in text_lower:
        region = "EU"

    confidence = 0.70 if value else 0.40
    if "kwh" in text_lower or "kilowatt" in text_lower:
        confidence = min(0.90, confidence + 0.15)

    dt = _guess_date(text)
    items = []
    if value:
        items.append(ExtractedItem(
            category="ENERGY",
            subcategory="grid_electricity",
            value=value,
            unit="KWH",
            phase="PRODUCTION",
            grid_region=region,
            recorded_at=dt,
            notes=f"Extracted from {filename}",
        ))
    return items, confidence


def _travel_manifest_extract(text: str, filename: str) -> Tuple[List[ExtractedItem], float]:
    """Extract travel distances from manifest."""
    text_lower = text.lower()
    nums = _extract_numbers(text)

    items = []
    # Look for flight indicators
    if any(w in text_lower for w in ["flight", "air", "passenger", "manifest"]):
        # Count passengers / flights roughly
        pax = None
        for n in nums:
            if 1 <= n <= 500:
                pax = int(n)
                break

        # Assume average short-haul distance per passenger if no explicit km
        km_value = None
        for n in nums:
            if 100 <= n <= 20000:
                km_value = n
                break

        # If we found km, use it; otherwise assume 800 km per passenger as placeholder
        if km_value:
            items.append(ExtractedItem(
                category="TRANSPORT",
                subcategory="short_haul_flight",
                value=km_value,
                unit="KM",
                phase="PRE_PRODUCTION",
                recorded_at=_guess_date(text),
                notes=f"Extracted from {filename}",
            ))
            confidence = 0.72
        elif pax:
            items.append(ExtractedItem(
                category="TRANSPORT",
                subcategory="short_haul_flight",
                value=Decimal(str(pax * 800)),
                unit="KM",
                phase="PRE_PRODUCTION",
                recorded_at=_guess_date(text),
                notes=f"Estimated {pax} pax × 800 km from {filename}",
            ))
            confidence = 0.55
        else:
            confidence = 0.35
    else:
        confidence = 0.30

    return items, confidence


def _hotel_invoice_extract(text: str, filename: str) -> Tuple[List[ExtractedItem], float]:
    """Extract hotel nights from invoice."""
    text_lower = text.lower()
    nums = _extract_numbers(text)

    # Look for nights or rooms
    nights = None
    for n in nums:
        if 1 <= n <= 5000:
            nights = n
            break

    confidence = 0.60 if nights else 0.35
    if "night" in text_lower or "room" in text_lower or "accommodation" in text_lower:
        confidence = min(0.88, confidence + 0.15)

    items = []
    if nights:
        items.append(ExtractedItem(
            category="ACCOMMODATION",
            subcategory="hotel",
            value=nights,
            unit="NIGHTS",
            phase="PRODUCTION",
            recorded_at=_guess_date(text),
            notes=f"Extracted from {filename}",
        ))
    return items, confidence


def _catering_invoice_extract(text: str, filename: str) -> Tuple[List[ExtractedItem], float]:
    """Extract catering items from invoice."""
    text_lower = text.lower()
    nums = _extract_numbers(text)
    items = []

    # Simple keyword-based item detection
    mappings = [
        ("beef", "beef", "KG"),
        ("lamb", "lamb", "KG"),
        ("chicken", "chicken", "KG"),
        ("pork", "pork", "KG"),
        ("fish", "fish", "KG"),
        ("vegetable", "vegetables", "KG"),
        ("rice", "rice", "KG"),
        ("bread", "bread", "KG"),
        ("dairy", "dairy_milk", "KG"),
        ("egg", "eggs", "KG"),
    ]

    found_any = False
    for keyword, subcat, unit in mappings:
        if keyword in text_lower:
            # Pick a plausible weight
            val = None
            for n in nums:
                if 1 <= n <= 5000:
                    val = n
                    break
            if val:
                found_any = True
                items.append(ExtractedItem(
                    category="CATERING",
                    subcategory=subcat,
                    value=val,
                    unit=unit,
                    phase="PRODUCTION",
                    recorded_at=_guess_date(text),
                    notes=f"Extracted from {filename}",
                ))

    confidence = 0.70 if found_any else 0.35
    return items, confidence


def _waste_ticket_extract(text: str, filename: str) -> Tuple[List[ExtractedItem], float]:
    """Extract waste weights from ticket."""
    text_lower = text.lower()
    nums = _extract_numbers(text)

    # Detect waste type
    subcategory = "landfill_general"
    if "recycl" in text_lower:
        subcategory = "recycling_mixed"
    elif "compost" in text_lower:
        subcategory = "compost"
    elif "incinerat" in text_lower:
        subcategory = "incineration"

    # Find weight
    weight = None
    for n in nums:
        if 1 <= n <= 50000:
            weight = n
            break

    confidence = 0.72 if weight else 0.40
    if "kg" in text_lower or "tonne" in text_lower or "weight" in text_lower:
        confidence = min(0.90, confidence + 0.12)

    items = []
    if weight:
        items.append(ExtractedItem(
            category="WASTE",
            subcategory=subcategory,
            value=weight,
            unit="KG",
            phase="PRODUCTION",
            recorded_at=_guess_date(text),
            notes=f"Extracted from {filename}",
        ))
    return items, confidence


def _generic_extract(text: str, filename: str) -> Tuple[List[ExtractedItem], float]:
    """Fallback generic extraction."""
    return [], 0.25


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

DOC_TYPE_HANDLERS = {
    "FUEL_RECEIPT": _fuel_receipt_extract,
    "ELECTRICITY_BILL": _electricity_bill_extract,
    "TRAVEL_MANIFEST": _travel_manifest_extract,
    "CATERING_INVOICE": _catering_invoice_extract,
    "WASTE_TICKET": _waste_ticket_extract,
    "HOTEL_INVOICE": _hotel_invoice_extract,
    "EPD": _generic_extract,
    "OTHER": _generic_extract,
}


def extract_document(doc_type: str, raw_text: str, filename: str) -> Dict[str, Any]:
    """
    Run extraction on a document.
    Returns: {"items": [...], "confidence": 0.0-1.0, "model": str}
    """
    # Try LLM first
    llm_result = extract_with_llm(doc_type, raw_text, filename)
    if llm_result.get("items") and llm_result.get("confidence", 0) >= 0.6:
        return llm_result

    # Fallback to heuristic
    handler = DOC_TYPE_HANDLERS.get(doc_type, _generic_extract)
    items, confidence = handler(raw_text, filename)

    return {
        "items": [
            {
                "category": i.category,
                "subcategory": i.subcategory,
                "value": float(i.value),
                "unit": i.unit,
                "phase": i.phase,
                "grid_region": i.grid_region,
                "recorded_at": i.recorded_at.isoformat() if i.recorded_at else None,
                "notes": i.notes,
            }
            for i in items
        ],
        "confidence": round(confidence, 2),
        "model": "heuristic-v1",
    }
