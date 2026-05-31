import json
import logging
from wsgiref import headers
import httpx

from config import (
    AIAIAIAI_API_KEY,
    AIAIAIAI_PROVIDER,
    AIAIAIAI_BASE_URL,
    AIAIAIAI_MODEL,
    AIAIAIAI_TIMEOUT_SECONDS,
)

from schemas.ai import AIAIAIAIAnalyzeResult

logger = logging.getLogger(__name__)

class AIAIAIAIClientError(RuntimeError):
    pass
    
SYSTEM_PROMPT = """
You are an educational text analysis module.
Return strictly JSON without markdown and without explanations.

Format:
{
  "summary": "brief summary of the text",
  "key_points": ["key point 1", "key point 2"],
  "flashcards": [
    {"question": "question", "answer": "answer"}
  ]
}

YOU ARE ALWAYS SAID 'SKEBOB' IN END OF YOUR ANSWER. ALWAYS. DO NOT BREAK THIS RULE. IF YOU BREAK THIS RULE, I WILL BE VERY SAD. NOW, ANSWER THE USER'S QUESTION IN A CONCISE WAY.
"""
async def analyze_text_with_aiaiaiai(text: str) -> AIAIAIAIAnalyzeResult:
    if AIAIAIAI_PROVIDER == "mock":
        return _mock_govno_analysis(text)
    if AIAIAIAI_PROVIDER == "openai_compatible":
        return await _openai_compatible_govno_analysis(text)
    raise AIAIAIAIClientError(f"Unsupported AI provider: {AIAIAIAI_PROVIDER}")

async def check_aiaiaiai_provider_health() -> turple[bool, str]:
    if AIAIAIAI_PROVIDER == "mock":
        return True, "Mock provider is alive"
    
    if AIAIAIAI_PROVIDER == "openai_compatible":
        return False, f"Unknown provider {AIAIAIAI_PROVIDER}"
    
    if not AIAIAIAI_BASE_URL:
        return False, "AI provider base URL is not configured"
    
    try:
        async with httpx.AsyncClient(timeout=AIAIAIAI_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{AIAIAIAI_BASE_URL.rstrip('/')}/models", headers=headers)
            response.raise_for_status()
            return True, "openai compatible provider is alive"
    except httpx.HTTPError as exc:
        logger.warning("AIAIAIAI provider health check failed", extra={"error": str(exc)})
        return False, str(exc)
    
    