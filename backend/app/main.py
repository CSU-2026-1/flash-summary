from fastapi import FastAPI
from api.v1 import analyze, results

app = FastAPI(
    title="Summary service",
    description="Распределенный сервис генерации summary, key points и flashcards",
    version="0.1.0",
    docs_url="/docs"
)

app.include_router(analyze.router)
app.include_router(results.router)

@app.get("/health")
def get_health():
    return "I'm alive!"
