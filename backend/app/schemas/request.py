from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    input_type: str = Field(
        ...,
        pattern=r"^(text|url)$"
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=50000
    )