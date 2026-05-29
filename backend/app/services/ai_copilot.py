"""
AI Copilot — conversational assistant for Terra.
Handles multi-turn chat with optional production context.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from . import ai_client
from .. import crud


SYSTEM_COPILOT = """You are Terra, a carbon accounting assistant for film and TV productions. Help users understand their emissions, find reduction opportunities, and navigate the platform. Be concise and actionable."""


def chat(db: Session, messages: List[Dict[str, str]], context_production_id: Optional[str] = None) -> dict:
    if not ai_client.is_configured():
        return {"error": "AI not configured", "reply": "AI is not configured. Set LLM_API_KEY or Azure OpenAI credentials."}

    context = ""
    if context_production_id:
        prod = crud.get_production(db, context_production_id)
        if prod:
            context = f"Current production: {prod.title} ({prod.type}). "

    msgs = [{"role": "system", "content": SYSTEM_COPILOT + "\n" + context}]
    msgs.extend(messages)

    out = ai_client.chat(msgs, temperature=0.4, max_tokens=2000)
    return {"reply": out.text, "model": out.model}
