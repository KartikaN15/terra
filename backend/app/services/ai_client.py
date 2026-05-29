"""
Unified AI client gateway.
All AI features (copilot chat, reduction planning, anomaly explainer, document extractor) call through here so:
- We never sprinkle `litellm.completion(...)` calls across the codebase.
- Provider switching (Azure OpenAI vs generic OpenAI) happens in one place.
"""
import json
import os
from typing import List, Dict, Any, Optional, Generator


class AIUnavailableError(Exception):
    pass


class AIResponse:
    def __init__(self, text: str, model: str):
        self.text = text
        self.model = model


def is_configured() -> bool:
    return bool(os.getenv("LLM_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY"))


def _provider_kwargs() -> Dict[str, Any]:
    from app.config import settings
    if settings.azure_openai_endpoint and settings.azure_openai_api_key:
        return {
            "model": f"azure/{settings.azure_openai_deployment or 'gpt-4o-mini'}",
            "api_base": settings.azure_openai_endpoint,
            "api_key": settings.azure_openai_api_key,
            "api_version": settings.azure_openai_api_version,
        }
    return {
        "model": settings.llm_model,
        "api_key": settings.llm_api_key,
    }


def chat(messages: List[Dict[str, str]], response_format: Optional[Dict[str, str]] = None, temperature: float = 0.2, max_tokens: int = 1500) -> AIResponse:
    try:
        import litellm
    except ImportError:
        raise AIUnavailableError("litellm package not installed")
    kwargs = _provider_kwargs()
    kwargs["messages"] = messages
    kwargs["temperature"] = temperature
    kwargs["max_tokens"] = max_tokens
    if response_format:
        kwargs["response_format"] = response_format
    response = litellm.completion(**kwargs)
    content = response.choices[0].message.content or ""
    return AIResponse(text=content, model=response.model or kwargs.get("model", "unknown"))


def stream_chat(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1500) -> Generator[str, None, None]:
    try:
        import litellm
    except ImportError:
        raise AIUnavailableError("litellm package not installed")
    kwargs = _provider_kwargs()
    kwargs["messages"] = messages
    kwargs["temperature"] = temperature
    kwargs["max_tokens"] = max_tokens
    kwargs["stream"] = True
    response = litellm.completion(**kwargs)
    for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta


def parse_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    return json.loads(text)
