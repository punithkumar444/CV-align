from pydantic import BaseModel
from typing import List

class EvaluationFeedback(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    role_fit_explanations: List[str]

class CVEvaluationResponse(BaseModel):
    relevance_score: float  # e.g., score between 0 and 1
    feedback: EvaluationFeedback
