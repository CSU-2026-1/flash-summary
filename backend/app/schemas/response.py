from pydantic import BaseModel, Field
from typing import List, Literal
from uuid import UUID

class Flashcard(BaseModel):
    question: str
    answer: str

class TaskStatusResponse(BaseModel):
    status: Literal["pending", "pending"]
    task_id: UUID

class ResultResponse(BaseModel):
    summary: str
    key_points: List[str]
    flashcards: List[Flashcard]