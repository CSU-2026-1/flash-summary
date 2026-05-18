import aio_pika
import logging
import asyncio

from config import RABBITMQ_URL, QUEUE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

async def handle_message(message: aio_pika.IncomingMessage) -> None:
    """
    TODO: Обрабатывает сообщение из очереди
    """

    logger.info(f"[*] Received {message}")

async def main() -> None:
    """
    Подключается к RabbitMQ и слушает очередь
    """

    connection = await aio_pika.connect(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1) # Ровно одна задача
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        logger.info(f"[*] Waiting for messages from {QUEUE_NAME}...")

        async with queue.iterator() as iterator:
            async for message in iterator:
                async with message.process(requeue=True):
                    await handle_message(message)


if __name__ == "__main__":
    asyncio.run(main())
