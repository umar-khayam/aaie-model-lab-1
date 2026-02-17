"""
app/api/feedback.py - Feedback evaluation routes
"""

import logging
from fastapi import APIRouter, HTTPException, status
from .schemas import FeedbackEvaluationRequest, EvaluationResponse
from ..services.feedback_generator import FeedbackQualityEvaluator
from ..utils.parsing import validate_feedback_entry

router = APIRouter(tags=["feedback"])
logger = logging.getLogger(__name__)


@router.post(
    "/evaluate-feedback",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Educator Feedback Quality",
    description="Evaluates a batch of educator feedback entries for quality, accuracy, and effectiveness."
)
def evaluate_feedback(request: FeedbackEvaluationRequest) -> EvaluationResponse:
    """
    Evaluate the quality of educator-style feedback.
    
    This endpoint:
    1. Accepts a batch of feedback entries
    2. Evaluates each using criterion-aligned metrics
    3. Returns individual scores and summary statistics
    
    Args:
        request: FeedbackEvaluationRequest with feedback entries and model choice
        
    Returns:
        EvaluationResponse with results and summary statistics
        
    Raises:
        HTTPException: On validation or evaluation errors
    """
    try:
        logger.info(f"Received request with {len(request.data)} feedback entries")
        
        # Convert Pydantic models to dictionaries for processing
        entries = [entry.dict() for entry in request.data]
        
        # Validate each entry
        for entry in entries:
            try:
                validate_feedback_entry(entry)
            except ValueError as e:
                logger.error(f"Validation error for entry {entry.get('index')}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid entry: {str(e)}"
                )
        
        # Initialize evaluator with specified model
        evaluator = FeedbackQualityEvaluator(model=request.model)
        logger.info(f"Evaluating with model: {request.model}")
        
        # Evaluate all entries
        results = evaluator.evaluate(entries)
        
        # Generate summary
        summary = evaluator.summary(results)
        
        logger.info(f"Evaluation complete. Mean score: {summary['mean_score']}")
        
        # Format response
        response = EvaluationResponse(
    results=[
        {
            "index": r["index"],
            "feedback_quality_score": r["feedback_quality_score"],
            "reasoning": r["reasoning"],
            "evaluation_steps": (
                "\n".join(r.get("evaluation_steps", []))
                if isinstance(r.get("evaluation_steps"), list)
                else r.get("evaluation_steps")
            ),
        }
        for r in results
    ],
    summary=summary,
)

        
        return response

    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error during evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check"
)
def health_check() -> dict:
    """
    Basic health check endpoint.
    
    Returns:
        Status dictionary
    """
    logger.info("Health check requested")
    return {"status": "ok", "service": "Educator Feedback Quality API"}