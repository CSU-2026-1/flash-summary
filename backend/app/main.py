import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.v1 import analyze, results
from containers.container import Container
from core.database import init_db, engine
from core.redis import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

container = Container()
container.wire(packages=["api.v1"])

@asynccontextmanager
async def lifespan(app: FastAPI):

    # TODO: Подключение к Postgres и Redis
    await init_db()

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

app.include_router(analyze.router)
app.include_router(results.router)