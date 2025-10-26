from pydantic import BaseModel
from typing import List


class PredictionRequest(BaseModel):
    threshold: float = 0.5


class PredictionResponse(BaseModel):
    classes: List[str]
    probabilities: List[float]
    active: List[str]
    quota_remaining: int



