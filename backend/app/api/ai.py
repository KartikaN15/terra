"""
AI API Endpoints
Mounts the ai_strategist + ai_copilot services onto FastAPI.
All routes guard on ai_client.is_configured() so the API returns a clean 503
when no LLM provider is set up.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from ..database import get_db
from ..services import ai_client, ai_copilot, ai_strategist
from .. import schemas

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/status")
def ai_status():
    return {
        "configured": ai_client.is_configured(),
        "provider": "azure" if (ai_client.is_configured() and __import__("app.config", fromlist=["settings"]).settings.azure_openai_endpoint) else ("openai" if ai_client.is_configured() else None),
    }


@router.post("/productions/{production_id}/reduction-plan")
def reduction_plan(production_id: str, db: Session = Depends(get_db)):
    if not ai_client.is_configured():
        raise HTTPException(status_code=503, detail="AI not configured")
    return ai_strategist.reduction_plan(db, production_id)


@router.post("/productions/{production_id}/executive-summary")
def executive_summary(production_id: str, db: Session = Depends(get_db)):
    if not ai_client.is_configured():
        raise HTTPException(status_code=503, detail="AI not configured")
    def _stream():
        for delta in ai_strategist.executive_summary_stream(db, production_id):
            yield delta
    from fastapi.responses import StreamingResponse
    return StreamingResponse(_stream(), media_type="text/plain")


class ParseEventRequest(schemas.BaseModel):
    text: str
    default_region: str = "UK"


@router.post("/parse-event")
def parse_event(req: ParseEventRequest):
    if not ai_client.is_configured():
        raise HTTPException(status_code=503, detail="AI not configured")
    return ai_strategist.parse_free_text_event(req.text, req.default_region)


class AnomalyExplainRequest(schemas.BaseModel):
    event_id: str
    baseline_kgco2e: float
    multiple_of_baseline: float
    peer_context: Optional[str] = None


@router.post("/explain-anomaly")
def explain_anomaly(req: AnomalyExplainRequest, db: Session = Depends(get_db)):
    if not ai_client.is_configured():
        raise HTTPException(status_code=503, detail="AI not configured")
    from .. import crud, models
    event = crud.get_event(db, req.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return ai_strategist.explain_anomaly(
        event, req.baseline_kgco2e, req.multiple_of_baseline, req.peer_context or ""
    )


class ChatRequest(schemas.BaseModel):
    messages: List[Dict[str, str]]
    context_production_id: Optional[str] = None


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    if not ai_client.is_configured():
        raise HTTPException(status_code=503, detail="AI not configured")
    msgs = req.messages
    return ai_copilot.chat(db, msgs, context_production_id=req.context_production_id)
