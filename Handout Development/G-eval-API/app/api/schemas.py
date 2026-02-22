"""
app/api/schemas.py - Pydantic data models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List


class FeedbackEntry(BaseModel):
    """Single feedback entry for evaluation"""
    index: int
    quality: Optional[float] = None
    authorship: Optional[str] = None
    criterion_scores: Dict[str, float]
    criterion_feedback: Dict[str, str]
    weighted_score_percent: Optional[float] = None
    feedback: str

    @validator('criterion_scores')
    def validate_criterion_scores(cls, v):
        """Ensure all scores are between 0 and 10"""
        for key, score in v.items():
            if not isinstance(score, (int, float)):
                raise ValueError(f"Score for '{key}' must be numeric")
            if not 0 <= score <= 10:
                raise ValueError(f"Score for '{key}' must be between 0 and 10, got {score}")
        return v

    @validator('weighted_score_percent')
    def validate_weighted_score(cls, v):
        """Ensure weighted score is between 0 and 100"""
        if v is not None and not (0 <= v <= 100):
            raise ValueError(f"weighted_score_percent must be between 0 and 100, got {v}")
        return v


class FeedbackEvaluationRequest(BaseModel):
    """Request payload for feedback evaluation"""
    data: List[FeedbackEntry]
    model: Optional[str] = Field(default="gpt-4o", description="LLM model to use for evaluation")

    @validator('data')
    def validate_data_not_empty(cls, v):
        """Ensure at least one feedback entry"""
        if not v:
            raise ValueError("At least one feedback entry is required")
        return v


from typing import Union, List

class EvaluationResult(BaseModel):
    index: int
    feedback_quality_score: float
    reasoning: str
    evaluation_steps: Optional[Union[str, List[str]]] = None



class EvaluationSummary(BaseModel):
    """Summary statistics for batch evaluations"""
    total_evaluations: int
    successful_evaluations: int
    failed_evaluations: int
    mean_score: float
    min_score: float
    max_score: float
    scores: List[float]


class EvaluationResponse(BaseModel):
    """Complete evaluation response"""
    results: List[EvaluationResult]
    summary: EvaluationSummary