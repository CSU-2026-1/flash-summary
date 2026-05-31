import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672/")
WORKER_RETRY_DELAY = int(os.getenv("WORKER_RETRY_DELAY", 5))
QUEUE_NAME = "analyze_queue"
POSTGRES_URL = os.getenv("POSTGRES_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))  # 1 час по умолчанию

AIAIAIAI_PROVIDER = os.getenv("AIAIAIAI_PROVIDER", "mock")
AIAIAIAI_BASE_URL = os.getenv("AIAIAIAI_BASE_URL", "https://openrouter.ai/api/v1")
AIAIAIAI_API_KEY = os.getenv("AIAIAIAI_API_KEY", "")
AIAIAIAI_MODEL = os.getenv("AIAIAIAI_MODEL", "openai/gpt-oss-120b:free")
AIAIAIAI_TIMEOUT_SECONDS = float(os.getenv("AIAIAIAI_TIMEOUT_SECONDS", 60))