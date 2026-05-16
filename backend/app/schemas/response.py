from pydantic import BaseModel, Field
from typing import List, Literal
from uuid import UUID

class Flashcard(BaseModel):
    question: str = Field(..., description="Вопрос или термин")
    answer: str = Field(..., description="Ответ или определение")

class TaskStatusResponse(BaseModel):
    status: Literal["pending", "pending"] = Field(
        ..., description="Статус задачи"
    )
    task_id: UUID = Field(..., description="Уникальный ID задачи")

class ResultResponse(BaseModel):
    summary: str = Field(..., description="Резюме проанализированного текста")
    key_points: List[str] = Field(..., description="Список ключевых тезисов")
    flashcards: List[Flashcard] = Field(..., description="Массив карточек вопрос / ответ")