from pydantic import BaseModel, Field

class LLMRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)

class LLMResponse(BaseModel):
    model: str
    prompt: str
    response: str
    input_characters: int
    output_characters: int