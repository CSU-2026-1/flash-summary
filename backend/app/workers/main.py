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


async def update_failed_message(message: aio_pika.Message, content: str) -> None:
    try:
        payload = json.loads(message.body.decode("utf-8"))

        async with AsyncSessionLocal() as session:
            task = await TaskRepository.get_by_id(session, payload["task_id"])

            if task:
                await TaskRepository.update_status(session, task, TaskStatus.failed)
                await set_task_status(content, payload["task_id"], "failed")

    except Exception as e:
        logger.error(f"[x] Error updating task status: {e}")


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    payload = json.loads(message.body.decode("utf-8"))
    task_id = payload["task_id"]
    content = payload["content"]

    logger.info(f"[x] Received {payload}")

    async with AsyncSessionLocal() as session:
        task = await TaskRepository.get_by_id(session, task_id)

        if not task:
            logger.error(f"[x] Task {task_id} not found in DB")
            return

        if message.headers.get("x-retry-count", 0) == 0:
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


async def loop() -> None:
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)

            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)

                dlx_name = f"{QUEUE_NAME}_dlx"
                await channel.declare_exchange(dlx_name, aio_pika.ExchangeType.FANOUT)

                dlq_name = f"{QUEUE_NAME}_dlq"
                dlq = await channel.declare_queue(dlq_name, durable=True)
                await dlq.bind(dlx_name)

                queue = await channel.declare_queue(
                    QUEUE_NAME,
                    durable=True,
                    arguments={"x-dead-letter-exchange": dlx_name},
                )

                logger.info(f"[*] Waiting for messages from {QUEUE_NAME}...")

                async with queue.iterator() as iterator:
                    async for message in iterator:
                        try:
                            await handle_message(message)
                            await message.ack()

                        except json.JSONDecodeError as e:
                            logger.error(f"[x] Invalid JSON in message: {e}")
                            await message.reject(requeue=False)

                        except Exception as e:
                            retry_count = message.headers.get("x-retry-count", 0)

                            if retry_count < 5:
                                logger.warning(
                                    f"[x] Error processing message: {e}. Retrying ({retry_count + 1}/5)..."
                                )

                                new_headers = dict(message.headers)
                                new_headers["x-retry-count"] = retry_count + 1

                                await channel.default_exchange.publish(
                                    aio_pika.Message(
                                        body=message.body,
                                        content_type=message.content_type,
                                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                        headers=new_headers,
                                    ),
                                    routing_key=QUEUE_NAME,
                                )

                                await message.ack()
                            else:
                                logger.error(
                                    f"[x] Error processing message: {e}. Max retries reached, sending to DLQ."
                                )

                                await update_failed_message(message, payload["content"])
                                await message.reject(requeue=False)

        except asyncio.CancelledError:
            logger.info("[*] Worker is shutting down...")
            break

        except Exception as e:
            logger.error(
                f"[x] Connection to RabbitMQ lost: {e}. Retrying in {WORKER_RETRY_DELAY} seconds..."
            )
            await asyncio.sleep(WORKER_RETRY_DELAY)


async def main() -> None:
    try:
        await loop()
    finally:
        pass


if __name__ == "__main__":
    asyncio.run(main())