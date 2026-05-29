"""
AI Strategist
Generates reduction plans, parses free-text events, and explains anomalies.
All calls through `ai_client` so provider routing (Azure / OpenAI) stays in one place.
"""
from decimal import Decimal
from typing import List, Dict, Any, Generator, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from . import ai_client
from .. import models, crud


SYSTEM_REDUCE = """You are Terra's Sustainability Strategist. Given production carbon data, suggest specific, measurable reduction actions."""

SYSTEM_PARSE = """You are a carbon accounting assistant. Extract structured activity data from free-text descriptions."""

SYSTEM_EXPLAIN = """You are a carbon accounting analyst. Explain why an emission event is anomalous in plain English."""


def reduction_plan(db: Session, production_id: str) -> dict:
    if not ai_client.is_configured():
        return {"error": "AI not configured"}
    prod = crud.get_production(db, production_id)
    summary = crud.get_production_summary(db, production_id)
    prompt = f"Production: {prod.title if prod else 'Unknown'}\nSummary: {summary}\nSuggest 3 reduction actions."
    out = ai_client.chat(
        messages=[
            {"role": "system", "content": SYSTEM_REDUCE},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return {"production_id": production_id, "plan": out.text}


def executive_summary_stream(db: Session, production_id: str) -> Generator[str, None, None]:
    if not ai_client.is_configured():
        yield "AI not configured."
        return
    prod = crud.get_production(db, production_id)
    summary = crud.get_production_summary(db, production_id)
    prompt = f"Production: {prod.title if prod else 'Unknown'}\nSummary: {summary}\nWrite a 2-paragraph executive summary."
    yield from ai_client.stream_chat(
        messages=[
            {"role": "system", "content": SYSTEM_REDUCE},
            {"role": "user", "content": prompt},
        ],
    )


def parse_free_text_event(text: str, default_region: str = "UK") -> dict:
    if not ai_client.is_configured():
        return {"error": "AI not configured"}
    prompt = f"Extract activity event from: {text}\nDefault region: {default_region}"
    out = ai_client.chat(
        messages=[
            {"role": "system", "content": SYSTEM_PARSE},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    parsed = ai_client.parse_json(out.text)
    return {"parsed": parsed}


def explain_anomaly(event: models.ActivityEvent, baseline_kg: float, multiple: float, peer_context: str = "") -> dict:
    if not ai_client.is_configured():
        return {"error": "AI not configured"}
    prompt = (
        f"Event: {event.category} / {event.subcategory}\n"
        f"Observed: {float(event.kgco2e):.1f} kgCO2e\n"
        f"Baseline: {baseline_kg:.1f} kgCO2e ({multiple:.1f}x)\n"
        f"Context: {peer_context}\nExplain why this is anomalous."
    )
    out = ai_client.chat(
        messages=[
            {"role": "system", "content": SYSTEM_EXPLAIN},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return {"explanation": out.text}
