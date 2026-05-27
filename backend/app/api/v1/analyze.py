from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide
from schemas.request import AnalyzeRequest
from schemas.response import TaskStatusResponse
from services.analyze_service import process_analyze_request
from core.rabbitmq import TaskPublisher
from core.database import get_session
from containers.container import Container

router = APIRouter(prefix="/api/v1", tags=["analyze"])

@router.post(
    "/analyze",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Отправить текст или URL на анализ",
    description="Эндпоинт принимает текст или ссылку, создает задачу и возвращает task_id",
)
@inject
async def create_analysis(
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_session),
    publisher: TaskPublisher = Depends(Provide[Container.publisher]),
):
    response = await process_analyze_request(
        request=request,
        session=session,
        publisher=publisher,
    )

    return response