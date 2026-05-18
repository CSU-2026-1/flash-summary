import logging
import json

import aio_pika

from config import RABBITMQ_URL, QUEUE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def publish(payload: dict) -> None:
    """
    Отправляет сообщение в очередь
    """

    # В идеале держать соединение открытым, но это как нибудь в будущем

    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        logger.info(f"[*] Sending {message}")

        await channel.default_exchange.publish(message, QUEUE_NAME)
