import logging
import json

import aio_pika

from config import RABBITMQ_URL, QUEUE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskPublisher:
    def __init__(self, url: str | None = None, queue_name: str | None = None) -> None:
        self.url = url or RABBITMQ_URL
        self._queue_name = queue_name or QUEUE_NAME
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self) -> None:
        """
        Подключение к брокеру сообщений
        """

        if self._connection and not self._connection.is_closed:
            return

        self._connection = await aio_pika.connect_robust(self.url)
        self._channel = await self._connection.channel()
    
        await self._channel.declare_queue(self._queue_name, durable=True)

        logger.info(f"[*] Publisher connected to {self._queue_name}...")

    async def close(self) -> None:
        """
        Закрытие соединения с брокером сообщений
        """

        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info(f"[*] Publisher closed connection to {self._queue_name}...")

    async def publish(self, message: dict) -> None:
        """
        Отправка сообщения в очередь
        """

        if not self._connection or self._connection.is_closed:
            await self.connect()

        message = aio_pika.Message(
            body=json.dumps(message).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        await self._channel.default_exchange.publish(message, routing_key=self._queue_name)

        logger.info(f"[x] Published {message}")
