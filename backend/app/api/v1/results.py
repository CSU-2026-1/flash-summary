from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.response import ResultResponse, TaskStatusResponse
from services.analyze_service import get_task_result
from core.database import get_session
from uuid import UUID

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
    data = await get_task_result(task_id_str, session)

    if data.get("error") == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")

    if data.get("status") in ["pending", "processing"]:
        return {"status": data["status"], "task_id": task_id_str}

    if data.get("status") == "completed":
        return data["result"]

    raise HTTPException(status_code=500, detail="Internal error")