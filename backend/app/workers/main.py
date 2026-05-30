import aio_pika
import logging
import asyncio
import json
import uuid

from services.cache_service import set_cached_result, set_task_status
from config import RABBITMQ_URL, QUEUE_NAME, WORKER_RETRY_DELAY
from core.database import AsyncSessionLocal
from repositories.task_repository import TaskRepository
from repositories.result_repository import ResultRepository
from models.task import TaskStatus
from models.result import Result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    payload = json.loads(message.body.decode("utf-8"))
    logger.info(f"[x] Received {payload}")

    task_id = payload["task_id"]
    content = payload["content"]

    try:
        async with AsyncSessionLocal() as session:
            task = await TaskRepository.get_by_id(session, task_id)

            if not task:
                logger.error(f"[x] Task {task_id} not found in DB")
                return

            await TaskRepository.update_status(session, task, TaskStatus.processing)
            await set_task_status(content, task_id, "processing")

            # TODO: заменить на реальную обработку
            await asyncio.sleep(3)
            fake_result = Result(
                task_id=uuid.UUID(task_id),
                summary="Заглушка summary",
                key_points=["point 1", "point 2"],
                flashcards=[{"question": "q1", "answer": "a1"}],
            )
            await ResultRepository.create(session, fake_result)
            await TaskRepository.update_status(session, task, TaskStatus.completed)

            result_data = {
                "status": "completed",
                "task_id": task_id,
                "summary": fake_result.summary,
                "key_points": fake_result.key_points,
                "flashcards": fake_result.flashcards,
            }
            await set_cached_result(content, result_data)

        logger.info(f"[x] Task {task_id} is done")

    except Exception as e:
        logger.error(f"[x] Task {task_id} failed: {e}")
        async with AsyncSessionLocal() as session:
            task = await TaskRepository.get_by_id(session, task_id)
            if task:
                await TaskRepository.update_status(session, task, TaskStatus.failed)
                await set_task_status(content, task_id, "failed")
        raise

async def loop() -> None:
    while True:
        try:
            connection = await aio_pika.connect(RABBITMQ_URL)

            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)
                queue = await channel.declare_queue(QUEUE_NAME, durable=True)

                logger.info(f"[*] Waiting for messages from {QUEUE_NAME}...")

                async with queue.iterator() as iterator:
                    async for message in iterator:
                        async with message.process(requeue=True):
                            await handle_message(message)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"[x] Connection to RabbitMQ lost: {e}. Retrying in {WORKER_RETRY_DELAY} seconds...")
            await asyncio.sleep(WORKER_RETRY_DELAY)

async def main() -> None:
    try:
        await loop()
    finally:
        pass


if __name__ == "__main__":
    asyncio.run(main())