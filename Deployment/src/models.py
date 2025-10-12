from typing import Dict, Any
from pydantic import BaseModel

class SubmissionRequest(BaseModel):
    text: str
    metadata: Dict[str, Any] = {}

class ClassificationResponse(BaseModel):
    classification: str
    confidence: float

class RubricScoreResponse(BaseModel):
    conceptual: str
    application: str
    evaluation: str
    writing: str

class FeedbackResponse(BaseModel):
    feedback: str

class EvaluationResponse(BaseModel):
    classification: ClassificationResponse
    rubric_scores: RubricScoreResponse
    ai_feedback: str
