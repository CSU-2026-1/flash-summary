import uuid
import hashlib
from typing import Dict
from backend.app.schemas.request import AnalyzeRequest
from backend.app.schemas.response import ResultResponse
from backend.app.schemas.internal import QueueTaskPayload

# ИМИТАЦИЯ, todo ЗАМЕНИТЬ НА РЕДИСКУ И БД
tasks_db: Dict[str, str] = {}
results_db: Dict[str, ResultResponse] = {}
cache_db: Dict[str, str] = {}

def get_content_hash(content: str) -> str:
    return hashlib.md5(content.encode(encoding='utf-8')).hexdigest()

async def process_analyze_request(request: AnalyzeRequest):
    content_hash = get_content_hash(request.content)

    if content_hash in cache_db:
        existing_task_id = cache_db[content_hash]
        return {"status": "pending", "task_id": existing_task_id}

    task_id = str(uuid.uuid4())

    tasks_db[task_id] = "pending"

    queue_message = {
        "task_id": task_id,
        "type": "analyze",
        "input_type": request.input_type,
        "content": request.content
    }

    #TODO celery_app.send_task() или че вы там понапишите

    cache_db[content_hash] = task_id

    return {"status": "pending", "task_id": task_id}

async def get_task_result(task_id: str):
    status = tasks_db.get(task_id)
    if not status:
        return {"error": "not found"}

    if status == "pending":
        return {"status": "pending"}

    result = results_db.get(task_id)

    if result:
        return {"status": "done", "result": result.dict()}

    return {"status": "failed"}