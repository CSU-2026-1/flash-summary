from fastapi import APIRouter, status, Depends
from schemas.request import AnalyzeRequest
from schemas.response import TaskStatusResponse
from services.analyze_service import process_analyze_request
from core.rabbitmq import TaskPublisher
from core.dependencies import get_publisher

router = APIRouter(prefix="/api/v1", tags=["analyze"])

@router.post(
    "/analyze",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Отправить текст или URL на анализ",
    description="Эндпоинт принимает текст или ссылку, создает задачу и возвращает task_id"
)
async def create_analysis(request: AnalyzeRequest, publisher: TaskPublisher = Depends(get_publisher)):
    response = await process_analyze_request(request, publisher)
    return response