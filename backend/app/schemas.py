from typing import Dict, List
from pydantic import BaseModel, Field


class ModerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class ExplanationToken(BaseModel):
    token: str
    weight: float


class ModerateResponse(BaseModel):
    id: str
    label: str
    confidence: Dict[str, float]
    explanation: List[ExplanationToken]
