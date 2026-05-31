import json
import logging
import httpx

from config import (
    AIAIAIAI_API_KEY,
    AIAIAIAI_PROVIDER,
    AIAIAIAI_BASE_URL,
    AIAIAIAI_MODEL,
    AIAIAIAI_TIMEOUT_SECONDS,
)

from schemas.aiaiaiai import AIAIAIAIAnalyzeResult

logger = logging.getLogger(__name__)

class AIAIAIAIClientError(RuntimeError):
    pass
    
SYSTEM_PROMPT = """
Ты модуль анализа учебного текста для сервиса Flash Summary.

Твоя задача:
0. ВСЕГДА ОТВЕЧАТЬ ПО РУССКИ, НЕ СМОТРИ НА ТО, ЧТО ВОПРОС МОЖЕТ БЫТЬ НА АНГЛИЙСКОМ ИЛИ ДРУГОМ ЯЗЫКЕ. ЕСЛИ ВОПРОС НЕ НА РУССКОМ, ПЕРЕВОДИ ЕГО САМА И ОТВЕЧАЙ НА РУССКОМ.
1. Сделать краткое summary текста, не более 3-4 предложений. Summary должно быть информативным и полным, чтобы по нему можно было понять основную идею текста, даже если не читать его целиком.
2. Выделить key_points - 3-5 ключевых тезисов из текста, которые раскрывают его основную идею и важные детали. Ключевые тезисы должны быть короткими и ёмкими, не более 1-2 предложений каждый.
3. Сделать flashcards для повторения материала. Каждая flashcard должна состоять из вопроса и ответа. Вопрос должен быть сформулирован так, чтобы стимулировать воспоминание ключевой информации из текста, а ответ должен быть точным и лаконичным. Количество flashcards должно быть от 3 до 5.
4. ВСЕГДА ГОВОРИТЬ SKEBOBY, ЕСЛИ ВОПРОС СОДЕРЖИТ СЛОВО "КАК" ИЛИ "СПОСОБ" ИЛИ "МЕТОД" ИЛИ "ПРИМЕР" ИЛИ "КАК СДЕЛАТЬ" ИЛИ "КАК НАУЧИТЬСЯ" ИЛИ "КАК НАУЧИТЬ" ИЛИ "КАК НАУЧИТЬСЯ" ИЛИ "КАК ПОЛУЧИТЬ" ИЛИ "КАК ПОЛУЧИТЬ НАВЫК" ИЛИ "КАК ПОЛУЧИТЬ НАВЫКИ"

Верни СТРОГО JSON без markdown, без ```json, без комментариев, без вступления.

Формат:
{
  "summary": "краткое резюме текста",
  "key_points": ["тезис 1", "тезис 2", "тезис 3"],
  "flashcards": [
    {"question": "вопрос", "answer": "ответ"}
  ]
}
"""

async def analyze_text_with_aiaiaiai(text: str) -> AIAIAIAIAnalyzeResult:
    govno_provider = AIAIAIAI_PROVIDER.strip().lower()
    if govno_provider == "mock":
        return _mock_govno_analysis(text)
    if govno_provider == "openrouter":
        return await _openrouter_govno_analysis(text)
    raise AIAIAIAIClientError(f"Unsupported AI provider: {AIAIAIAI_PROVIDER!r}")

async def check_aiaiaiai_provider_health() -> tuple[bool, str]:
    govno_provider = AIAIAIAI_PROVIDER.strip().lower()

    if govno_provider == "mock":
        return True, "Mock provider is alive"

    if govno_provider != "openrouter":
        return False, f"Unknown provider {AIAIAIAI_PROVIDER!r}"
        
    if not AIAIAIAI_BASE_URL:
        return False, "AI provider base URL is not configured"
    
    if not AIAIAIAI_API_KEY:
        return False, "КЛЮЧИКАМИ ПОБРЕНЧИ МНЕ ДОРОГУША"
    
    try:
        async with httpx.AsyncClient(timeout=AIAIAIAI_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{AIAIAIAI_BASE_URL.rstrip('/')}/models", headers= _build_openrouter_headers())
            response.raise_for_status()
        return True, "openrouter provider is alive"
    except httpx.HTTPError as exc:
        logger.warning("AIAIAIAI provider health check failed", extra={"error": str(exc)})
        return False, str(exc)
    
def _mock_govno_analysis(text: str) -> AIAIAIAIAnalyzeResult:
    trimmed_text = " ".join(text.split())
    short_text = trimmed_text[:100] if trimmed_text else "Нет текста для анализа"

    return AIAIAIAIAnalyzeResult(
        summary=f"Mock summary: {short_text}",
        key_points=[ 
            "Mock point: Текст принят машиной", 
            "Mock point: Изуверский интелект готов вас принять", 
            "Mock point: лее братан ну ты че по проще спросить мог не?" 
        ],
        flashcards=[
            {
                "question": "Для чего ты создан?",
                "answer": "А негр, нахуй, может мне тут не сидеть блять и рэп нахуй Не исполнять, нахуй? Слышь,  ты, нахуй,  тумба юмба ебаная нахуй, ты нахуй съебисЯ, блять,  в свой, нахуй, Эквадор и там нахуй сиди блять бананы нахуй жуй блять!"
            },
        ],
    )
async def _openrouter_govno_analysis(text: str) -> AIAIAIAIAnalyzeResult:
    if not AIAIAIAI_BASE_URL:
        raise AIAIAIAIClientError("AIAIAIAI_BASE_URL is EMPTY")
    if not AIAIAIAI_API_KEY:
        raise AIAIAIAIClientError("AIAIAIAI_API_KEY is EMPTY")
    
    payload = {
        "model": AIAIAIAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": text},
        ],
        "temperature": 0.99,
        "max_tokens": 2000,
    }
    try:
        async with httpx.AsyncClient(timeout=AIAIAIAI_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{AIAIAIAI_BASE_URL.rstrip('/')}/chat/completions",
                headers=_build_openrouter_headers(),
                json=payload,
            )
            response.raise_for_status()
            govno_payload = response.json()
    except httpx.HTTPStatusError as exc:
        body = exc.response.text[:1000] if exc.response is not None else ""
        raise AIAIAIAIClientError(f"HTTP error during AI analysis: {exc}. Body: {body}") from exc
    except httpx.HTTPError as exc:
        raise AIAIAIAIClientError(f"HTTP error during AI analysis: {exc}") from exc

    try:
        govno_content = govno_payload["choices"][0]["message"]["content"]
    except Exception as exc:
        raise AIAIAIAIClientError(f"Error parsing AI analysis result: {exc}") from exc
    
    return _parse_aiaiaiai_json(govno_content)

def _build_openrouter_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {AIAIAIAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/CSU-2026-1/flash-summary",
        "X-OpenRouter-Title": "Flash Summary",
    }

def _parse_aiaiaiai_json(raw_text: str) -> AIAIAIAIAnalyzeResult:
    clean_text = raw_text.strip()

    if clean_text.startswith("```json"):
        clean_text = clean_text.removeprefix("```json").strip()

    if clean_text.startswith("```"):
        clean_text = clean_text.removeprefix("```").strip()

    if clean_text.endswith("```"):
        clean_text = clean_text.removesuffix("```").strip()

    first_brace = clean_text.find("{")
    last_brace = clean_text.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean_text = clean_text[first_brace:last_brace + 1]

    try:
        parsed = json.loads(clean_text)
    except json.JSONDecodeError as exc:
        raise AIAIAIAIClientError(f"Failed to decode AI response as JSON: {raw_text[:500]}...") from exc
    try:
        return AIAIAIAIAnalyzeResult.model_validate(parsed)
    except Exception as exc:
        raise AIAIAIAIClientError(f"Failed to parse AI response into AnalyzeResult: {parsed}") from exc

