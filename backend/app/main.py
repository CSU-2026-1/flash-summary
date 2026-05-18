import logging

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from api.v1 import analyze, results
from core.rabbitmq import TaskPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контейнер с контекстом для приложения
    """

    # TODO: Подключение к Postgres и Redis

    publisher = TaskPublisher()

    try:
        await publisher.connect()
        app.state.publisher = publisher
    except Exception as e:
        logger.error(f"RabbitMQ is not available: {e}. Recconecting in publisher...")
    
    try:
        yield
    finally:
        await publisher.close()

app = FastAPI(
    lifespan=lifespan,
    title="Summary service",
    description="Распределенный сервис генерации summary, key points и flashcards",
    version="0.1.0",
    docs_url="/docs"
)

app.include_router(analyze.router)
app.include_router(results.router)