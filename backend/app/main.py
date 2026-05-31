import logging
import socket

from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.v1 import analyze, results, aiaiaiai
# from backend.app.schemas import aiaiaiai
from containers.container import Container
from core.database import init_db, engine
from core.redis import redis_client
from core.app_logging import setup_logging

setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)

container = Container()
container.wire(packages=["api.v1"])

@asynccontextmanager
async def lifespan(app: FastAPI):

    # TODO: Подключение к Postgres и Redis
    # Инициализация бд теперь в алембике

    publisher = container.publisher()

    try:
        await publisher.connect()
    except Exception as e:
        logger.error(f"RabbitMQ is not available: {e}. Recconecting in publisher...")
    
    try:
        yield
    finally:
        await publisher.close()
        await redis_client.aclose()
        await engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    title="Summary service",
    description="Распределенный сервис генерации summary, key points и flashcards",
    version="0.1.0",
    docs_url="/docs"
)

app.container = container

SOCKET = socket.gethostname()

app.include_router(analyze.router)
app.include_router(results.router)
app.include_router(aiaiaiai.router)

@app.get(
    "/health",
    summary="Проверка работоспособности сервиса",
    description="Эндпоинт для проверки статуса сервиса и его окружения",
)
async def health_check():
    return {"status": "ok", "socket": SOCKET}