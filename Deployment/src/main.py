import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from google import genai
import os
from src.models import (
    SubmissionRequest,
    ClassificationResponse,
    RubricScoreResponse,
    FeedbackResponse,
    EvaluationResponse
)
from src.config.config import Config
from src.utils.response_parser import parse_classification, parse_rubric_scores, parse_feedback
from src.utils.logging.config import setup_logging

# Setup logging
logger = setup_logging()

# Verify logger is working
logger.info("Starting AAIE Model Lab API")

load_dotenv()
model_id = os.getenv("GOOGLE_MODEL_ID")
api_key = os.getenv("GOOGLE_API_KEY")

app = FastAPI()
client = genai.Client(api_key=api_key)
config = Config()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests and their processing time."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Status: {response.status_code} | "
        f"Processing Time: {process_time:.2f}ms"
    )
    return response

# Sample classifications list
classifications = ["Human", "AI Generated"]

def generate_response(prompt: str, system_prompt: str = "") -> str:
    """Generate a response from the LLM.
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt to guide the model's behavior
        
    Returns:
        The generated response text
    """
    try:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        logger.debug(f"Sending prompt to LLM: {full_prompt[:200]}...")
        
        start_time = time.time()
        response = client.models.generate_content(
            model=model_id,
            contents=full_prompt
        )
        process_time = (time.time() - start_time) * 1000
        
        logger.info(f"LLM response generated in {process_time:.2f}ms")
        logger.debug(f"LLM response: {response.text[:200]}...")
        
        return response.text
    except Exception as e:
        logger.error(f"Error generating LLM response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate LLM response"
        )

@app.get("/api/v1/llm-status")
async def llm_status() -> dict:
    return {"status": generate_response("""
        Please respond with 'OK' to confirm LLM is operational 
        and include llm metadata, eg: model version, platform, model cutoff date..
        """)}

@app.post("/api/v1/classify")
async def classify_submission(request: SubmissionRequest) -> ClassificationResponse:
    logger.info("Processing classification request")
    logger.debug(f"Input text length: {len(request.text)} characters")
    
    try:
        system_prompt = config.get_system_prompt("classify")
        response = generate_response(
            prompt=f"Text to classify:\n{request.text}",
            system_prompt=system_prompt
        )
        
        classification, confidence = parse_classification(response)
        logger.info(f"Classification result: {classification} with confidence: {confidence}")
        
        return ClassificationResponse(
            classification=classification,
            confidence=confidence
        )
    except ValueError as e:
        logger.error(f"Failed to parse classification response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in classification endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during classification"
        )

@app.post("/api/v1/rubric-score")
async def score_submission(request: SubmissionRequest) -> RubricScoreResponse:
    logger.info("Processing rubric scoring request")
    logger.debug(f"Input text length: {len(request.text)} characters")
    
    try:
        system_prompt = config.get_system_prompt("rubric")
        response = generate_response(
            prompt=f"Text to evaluate:\n{request.text}",
            system_prompt=system_prompt
        )
        
        scores = parse_rubric_scores(response)
        logger.info(f"Rubric scores generated: {scores}")
        
        return RubricScoreResponse(**scores)
    except ValueError as e:
        logger.error(f"Failed to parse rubric scores: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in rubric scoring endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during rubric scoring"
        )

@app.post("/api/v1/generate-feedback")
async def generate_feedback(request: SubmissionRequest) -> FeedbackResponse:
    logger.info("Processing feedback generation request")
    logger.debug(f"Input text length: {len(request.text)} characters")
    
    try:
        system_prompt = config.get_system_prompt("feedback")
        response = generate_response(
            prompt=f"Text to provide feedback on:\n{request.text}",
            system_prompt=system_prompt
        )
        
        feedback = parse_feedback(response)
        logger.info("Feedback generated successfully")
        logger.debug(f"Generated feedback: {feedback[:200]}...")
        
        return FeedbackResponse(feedback=feedback)
    except ValueError as e:
        logger.error(f"Failed to parse feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in feedback generation endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during feedback generation"
        )

@app.post("/api/v1/evaluate")
async def evaluate_submission(request: SubmissionRequest) -> EvaluationResponse:
    logger.info("Processing comprehensive evaluation request")
    logger.debug(f"Input text length: {len(request.text)} characters")
    
    try:
        # Get classification
        logger.debug("Starting classification step")
        classification = await classify_submission(request)
        
        # Get rubric scores
        logger.debug("Starting rubric scoring step")
        rubric_scores = await score_submission(request)
        
        # Generate feedback
        logger.debug("Starting feedback generation step")
        feedback = await generate_feedback(request)
        
        logger.info("Comprehensive evaluation completed successfully")
        return EvaluationResponse(
            classification=classification,
            rubric_scores=rubric_scores,
            ai_feedback=feedback.feedback
        )
    except Exception as e:
        logger.error(f"Unexpected error in comprehensive evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during comprehensive evaluation"
        )