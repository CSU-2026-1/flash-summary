from fastapi import APIRouter, status

from config import AIAIAIAI_PROVIDER, AIAIAIAI_BASE_URL, AIAIAIAI_API_KEY, AIAIAIAI_MODEL
from shemas.aiaiaiai import AIAIAIAIConfigResponse, AIAIAIAIHealthResponse
from services.ai_client import check_aiaiaiai_provider_health

router = APIRouter(prefix="api/v1/aiaiaiai", tags=["aiaiaiai"])

@router.get("/config", response_model=AIAIAIAIConfigResponse, 
            status_code=status.HTTP_200_OK, 
            summary="Получить текущую конфигурацию AI провайдера", 
            description="Эндпоинт возвращает информацию о текущем AI провайдере, включая его название, модель и статус конфигурации",
)
async def get_aiaiaiai_config():
    return AIAIAIAIConfigResponse(
        provider=AIAIAIAI_PROVIDER,
        model=AIAIAIAI_MODEL,
        base_url_condigured=bool(AIAIAIAI_BASE_URL),
        api_key_configured=bool(AIAIAIAI_API_KEY)
    )

@router.get(
    "/health", 
    response_model=AIAIAIAIHealthResponse, 
    status_code=status.HTTP_200_OK, 
    summary="Проверить здоровье AI провайдера", 
    description="Эндпоинт выполняет проверку доступности и работоспособности текущего AI провайдера и возвращает статус и сообщение о состоянии"
)
async def check_aiaiaiai_health():
    is_alive, message = await check_aiaiaiai_provider_health()

    return {
        "status": "ok" if is_alive else "error",
        "provider": AIAIAIAI_PROVIDER,
        "model": AIAIAIAI_MODEL,
        "message": message,
    }