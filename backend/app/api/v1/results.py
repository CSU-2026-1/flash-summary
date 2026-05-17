from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.response import ResultResponse, TaskStatusResponse
from backend.app.services.analyze_service import get_task_result
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
async def get_result(task_id: UUID):
    task_id_str = str(task_id)
    data = await get_task_result(task_id_str)

    if data.get("error") == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")

    if data.get("status") == "pending":
        return {"status": "pending", "task_id": task_id_str}

    if data.get("status") == "done":
        return data["result"]

    raise HTTPException(status_code=500, detail="Internal error")