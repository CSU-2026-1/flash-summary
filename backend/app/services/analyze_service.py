import hashlib
import uuid
from repositories.task_repository import TaskRepository
from repositories.result_repository import ResultRepository
from schemas.request import AnalyzeRequest
from schemas.internal import QueueTaskPayload
from models.task import Task, TaskStatus
from core.rabbitmq import TaskPublisher
from sqlalchemy.ext.asyncio import AsyncSession

def get_content_hash(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()

async def process_analyze_request(
    request: AnalyzeRequest,
    session: AsyncSession,
    publisher: TaskPublisher,
):

    task = Task(
        id=uuid.uuid4(),
        status=TaskStatus.pending,
        input_type=request.input_type,
        content=request.content,
    )

    await TaskRepository.create(session, task)

    queue_message = QueueTaskPayload(
        task_id=str(task.id),
        type="analyze",
        input_type=request.input_type,
        content=request.content,
    )

    await publisher.publish(queue_message.model_dump())

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