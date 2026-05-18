import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672/")
WORKER_RETRY_DELAY = int(os.getenv("WORKER_RETRY_DELAY", 5))
QUEUE_NAME = "analyze_queue"