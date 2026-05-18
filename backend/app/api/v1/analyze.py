from fastapi import APIRouter, status
from schemas.request import AnalyzeRequest
from schemas.response import TaskStatusResponse
from services.analyze_service import process_analyze_request

router = APIRouter(prefix="/api/v1", tags=["analyze"])

@router.post(
    "/analyze",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Отправить текст или URL на анализ",
    description="Эндпоинт принимает текст или ссылку, создает задачу и возвращает task_id"
)
async def create_analysis(request: AnalyzeRequest):
    response = await process_analyze_request(request)
    return response