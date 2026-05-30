import hashlib
import json
from core.redis import redis_client
from config import REDIS_TTL


def get_content_hash(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()


async def get_cached_result(content: str) -> dict | None:
    key = get_content_hash(content)
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def set_task_status(content: str, task_id: str, status: str) -> None:
    key = get_content_hash(content)
    await redis_client.set(key, json.dumps({
        "status": status,
        "task_id": task_id,
    }), ex=REDIS_TTL)


async def set_cached_result(content: str, result: dict) -> None:
    key = get_content_hash(content)
    await redis_client.set(key, json.dumps(result), ex=REDIS_TTL)