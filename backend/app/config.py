import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672/")
QUEUE_NAME = "analyze_queue"