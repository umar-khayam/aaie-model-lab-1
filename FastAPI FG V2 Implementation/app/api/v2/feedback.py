from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.feedback_generator import generate_feedback_results

router = APIRouter(prefix="/api/v2", tags=["Feedback"])

class PerformanceDescriptors(BaseModel):
    excellent: str
    good: str
    average: str
    needs_improvement: str
    poor: str

    class Config:
        extra = "forbid"

class Criterion(BaseModel):
    criterion_id: str
    name: str
    description: str
    performance_descriptors: PerformanceDescriptors
    weight: float = Field(..., ge=0, le=100)

    class Config:
        extra = "forbid"

class Rubric(BaseModel):
    rubric_id: str
    criteria: List[Criterion]

    class Config:
        extra = "forbid"

class Submission(BaseModel):
    final_submission: str = Field(..., min_length=50)
    quality: Optional[str] = None
    authorship: Optional[str] = None

    class Config:
        extra = "forbid"

class FeedbackRequest(BaseModel):
    domain: str
    assignment_description: str
    rubric: Rubric
    submission: Submission

    class Config:
        extra = "forbid"

class FeedbackResult(BaseModel):
    index: int
    quality: Optional[str]
    authorship: Optional[str]
    criterion_scores: dict
    criterion_feedback: dict
    weighted_score_percent: float
    feedback: str

@router.post("/evaluate", response_model=List[FeedbackResult])
def generate_feedback_v2(request: FeedbackRequest):
    results = generate_feedback_results(
        domain=request.domain,
        assignment_prompt=request.assignment_description,
        rubric=request.rubric.model_dump(),
        submissions=[request.submission.model_dump()]  # Wrapped in a list
    )

    return results

# # Previous version supporting multiple submissions
# @router.post("/evaluate", response_model=List[FeedbackResult])
# def generate_feedback_v2(request: FeedbackRequest):
#     results = generate_feedback_results(
#         domain=request.domain,
#         assignment_prompt=request.prompt,
#         rubric=request.rubric.dict(),
#         submissions=[s.dict() for s in request.submissions]
#     )
#     return results