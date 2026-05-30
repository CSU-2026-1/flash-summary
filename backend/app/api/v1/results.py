from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.response import ResultResponse, TaskStatusResponse
from services.analyze_service import get_task_result
from core.database import get_session
from uuid import UUID
import logging
from core.app_logging import task_id_var

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["results"])

@router.get(
    "/result/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить результат анализа",
    description="Возвращает summary, key_points и flashcards по task_id",
    responses={
        200: {"model": ResultResponse, "description": "Результат готов"},
        202: {"model": TaskStatusResponse, "description": "Задача в обработке"},
        404: {"description": "Задача не найдена"}
    }
)
async def get_result(task_id: UUID, session: AsyncSession = Depends(get_session)):
    task_id_str = str(task_id)
    task_id_var.set(task_id_str)

    data = await get_task_result(task_id_str, session)

    if data.get("error") == "not_found":
        logger.warning("Task not found", extra={"task_id": task_id_str})
        raise HTTPException(status_code=404, detail="Task not found")

    if data.get("status") in ["pending", "processing"]:
        return {"status": data["status"], "task_id": task_id_str}

    if data.get("status") == "completed":
        logger.info("Result returned", extra={"task_id": task_id_str})
        return data["result"]

    logger.error("Unexpected state", extra={"task_id": task_id_str, "status": data.get("status")})
    raise HTTPException(status_code=500, detail="Internal error")