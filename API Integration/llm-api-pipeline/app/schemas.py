
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Label = Literal["AI", "Human", "Hybrid"]
RatingLabel = Literal["excellent", "good", "average", "needs improvement", "poor"]

class PerformanceDescriptor(BaseModel):
    excellent: Optional[str] = None
    good: Optional[str] = None
    average: Optional[str] = None
    needs_improvement: Optional[str] = None
    poor: Optional[str] = None

class RubricCriterion(BaseModel):
    criterion_id: str
    name: str
    description: Optional[str] = None
    performance_descriptors: Optional[PerformanceDescriptor] = None

class Rubric(BaseModel):
    rubric_id: str
    criteria: List[RubricCriterion]

class EvalRequest(BaseModel):
    domain: str
    prompt: str
    rubric: Rubric
    submission: str
    actual_label: Optional[Label] = Field(default=None, description="Optional ground-truth for analysis")

class ClassificationResponse(BaseModel):
    """
    Response model for the classification endpoint.

    The service now returns the predicted label along with a confidence
    score. Rationale strings are no longer included in order to keep
    outputs concise and aligned with the latest specification.
    """
    label: Label
    confidence: float = Field(ge=0.0, le=1.0)

class ConfidenceResponse(BaseModel):
    """
    Response model for the confidence endpoint.

    Only the confidence value is returned; explanatory basis text has
    been dropped per the updated requirements.
    """
    confidence: float = Field(ge=0.0, le=1.0)

class CriterionRating(BaseModel):
    """
    Rating for a single rubric criterion.

    Each criterion returns a categorical rating (e.g. excellent, good,
    average, needs improvement, poor). Reasons are intentionally
    omitted to streamline the output.
    """
    criterion_id: str
    name: str
    rating: RatingLabel

class RubricScoresResponse(BaseModel):
    """
    Response model for rubric scores.

    Only the per‑criterion ratings are returned. The overall rating
    previously included has been removed in favour of individual
    criterion feedback.
    """
    scores: List[CriterionRating]

class OverallFeedbackResponse(BaseModel):
    """
    Response model for feedback endpoint.

    The feedback endpoint now returns a single string containing a
    narrative summary of the student’s performance and suggested
    improvements. Structured subfields (strengths, weaknesses,
    next_steps) are no longer used.
    """
    feedback: str
