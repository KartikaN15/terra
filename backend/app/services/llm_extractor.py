"""
LLM Document Extractor using LiteLLM.
Sends document text to an LLM and asks for structured JSON output.
"""
import os
import json
import re
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

EXTRACTION_PROMPT = """You are a carbon accounting assistant. Extract structured activity data from the following document text.

Document type: {doc_type}
Filename: {filename}

Document text:
---
{text}
---

Extract all measurable activities relevant to carbon footprint calculation. Return ONLY a JSON object in this exact format:

{{
  "items": [
    {{
      "category": "ENERGY|TRANSPORT|ACCOMMODATION|MATERIALS|WASTE|WATER|CATERING|POST_VFX",
      "subcategory": "specific type e.g. diesel_generator, short_haul_flight, hotel, beef, grid_electricity",
      "value": numeric_amount,
      "unit": "LITRES|KWH|KM|MILES|KG|HOURS|GBP|USD|TONNES|M3|NIGHTS",
      "phase": "DEVELOPMENT|PRE_PRODUCTION|PRODUCTION|POST_PRODUCTION|DISTRIBUTION",
      "grid_region": "UK|US|EU|Global",
      "recorded_at": "YYYY-MM-DD",
      "notes": "brief context"
    }}
  ],
  "confidence": 0.0-1.0,
  "model": "llm-extractor-v1"
}}

Rules:
- If the document is a fuel receipt, extract litres and fuel type.
- If electricity bill, extract kWh and region.
- If travel manifest, extract passenger count and distances.
- If hotel invoice, extract room nights.
- If catering, extract food items and weights.
- If waste ticket, extract weight and waste type.
- Use exact subcategory names from common production categories.
- Set confidence based on clarity of data.
- Return ONLY the JSON object, no markdown formatting.
"""


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def extract_with_llm(doc_type: str, raw_text: str, filename: str) -> Dict[str, Any]:
    from . import ai_client

    if not ai_client.is_configured():
        return {"items": [], "confidence": 0.0, "model": "llm-no-provider"}

    prompt = EXTRACTION_PROMPT.format(
        doc_type=doc_type,
        filename=filename,
        text=raw_text[:8000],
    )

    try:
        out = ai_client.chat(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2000,
        )
        parsed = ai_client.parse_json(out.text)

        items = []
        for item in parsed.get("items", []):
            try:
                value = Decimal(str(item.get("value", 0)))
                if value <= 0:
                    continue
                items.append({
                    "category": item.get("category", "OTHER"),
                    "subcategory": item.get("subcategory", "unknown"),
                    "value": float(value),
                    "unit": item.get("unit", "KG"),
                    "phase": item.get("phase", "PRODUCTION"),
                    "grid_region": item.get("grid_region") or "UK",
                    "recorded_at": _parse_date(item.get("recorded_at")),
                    "notes": item.get("notes", f"LLM extracted from {filename}"),
                })
            except Exception:
                continue

        return {
            "items": items,
            "confidence": float(parsed.get("confidence", 0.7)),
            "model": f"llm-{out.model}",
        }
    except Exception as e:
        return {"items": [], "confidence": 0.0, "model": f"llm-error: {str(e)[:50]}"}


def _parse_date(val) -> Optional[str]:
    if not val:
        return datetime.now(timezone.utc).isoformat()
    if isinstance(val, str):
        try:
            dt = datetime.strptime(val, "%Y-%m-%d")
            return dt.isoformat()
        except ValueError:
            return datetime.now(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()
