import uuid
from services.cache_service import get_cached_result, set_cached_result, set_task_status
from repositories.task_repository import TaskRepository
from repositories.result_repository import ResultRepository
from schemas.request import AnalyzeRequest
from schemas.internal import QueueTaskPayload
from models.task import Task, TaskStatus
from core.rabbitmq import TaskPublisher
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from core.app_logging import task_id_var

logger = logging.getLogger(__name__)

async def process_analyze_request(
    request: AnalyzeRequest,
    session: AsyncSession,
    publisher: TaskPublisher,
):
    cached = await get_cached_result(request.content)
    if cached:
        return {
            "status": cached.get("status", "completed"),
            "task_id": cached.get("task_id"),
        }

    logger.info("Cache MISS, creating task", extra={
        "input_type": request.input_type,
        "content_length": len(request.content)
    })

    task = Task(
        id=uuid.uuid4(),
        status=TaskStatus.pending,
        input_type=request.input_type,
        content=request.content,
    )

    await TaskRepository.create(session, task)
    await set_task_status(request.content, str(task.id), "pending")

    queue_message = QueueTaskPayload(
        task_id=str(task.id),
        type="analyze",
        input_type=request.input_type,
        content=request.content,
    )

    await publisher.publish(queue_message.model_dump())

    logger.info("Task published to queue", extra={
        "task_id": str(task.id),
        "queue_type": queue_message.type
    })

    return {
        "status": task.status,
        "task_id": str(task.id),
    }

async def get_task_result(
    task_id: str,
    session: AsyncSession,
):
    task = await TaskRepository.get_by_id(session, task_id)

    if not task:
        return {"error": "not_found"}

    if task.status in [TaskStatus.pending, TaskStatus.processing]:
        return {
            "status": task.status,
            "task_id": str(task.id),
        }

    if task.status == TaskStatus.failed:
        return {
            "status": "failed",
            "task_id": str(task.id),
        }

    result = await ResultRepository.get_by_task_id(session, task.id)

    if not result:
        return {"status": "failed"}

    return {
        "status": "completed",
        "result": {
            "task_id": str(task.id),
            "summary": result.summary,
            "key_points": result.key_points,
            "flashcards": result.flashcards,
        },
    }