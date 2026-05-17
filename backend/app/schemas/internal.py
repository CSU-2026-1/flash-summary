from pydantic import BaseModel
from typing import Literal

class QueueTaskPayload(BaseModel):
    task_id: str
    type: Literal["analyze"]
    input_type: str
    content: str