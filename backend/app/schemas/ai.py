from pydantic import BaseModel, Field

class AIAIAIAIFlashcard(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)

class AIAIAIAIAnalyzeRequest(BaseModel):
    summary: str = Field(..., min_length=1)
    key_points: list[str] = Field(default_factory=list)
    flashcards: list[AIAIAIAIFlashcard] = Field(default_factory=list)

class AIAIAIAIConfigResponse(BaseModel):
    provider: str
    model: str
    base_url_condigured: bool
    api_key_configured: bool

class AIAIAIAIHealthResponse(BaseModel):
    status: str
    provider: str
    model: str
    message: str
