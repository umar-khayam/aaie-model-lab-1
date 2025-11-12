
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import (
    EvalRequest,
    ClassificationResponse,
    ConfidenceResponse,
    RubricScoresResponse,
    OverallFeedbackResponse,
)
from app.services.evaluator import EvaluatorService

app = FastAPI(title="LLM Evaluation Pipeline", version="1.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
svc = EvaluatorService()

@app.post("/api/v1/classification", response_model=ClassificationResponse)
async def classification(req: EvalRequest):
    try:
        data = await svc.classify(req.domain, req.prompt, req.rubric.model_dump(), req.submission)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/confidence", response_model=ConfidenceResponse)
async def confidence(req: EvalRequest):
    try:
        data = await svc.confidence(req.domain, req.prompt, req.rubric.model_dump(), req.submission)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rubric-scores", response_model=RubricScoresResponse)
async def rubric_scores(req: EvalRequest):
    try:
        data = await svc.rubric_scores(req.domain, req.prompt, req.rubric.model_dump(), req.submission)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback", response_model=OverallFeedbackResponse)
async def feedback(req: EvalRequest):
    try:
        data = await svc.feedback(req.domain, req.prompt, req.rubric.model_dump(), req.submission)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/evaluate")
async def evaluate(req: EvalRequest):
    try:
        data = await svc.evaluate(req.domain, req.prompt, req.rubric.model_dump(), req.submission)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

