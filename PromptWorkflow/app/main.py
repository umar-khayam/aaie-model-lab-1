"""
Minimal FastAPI app to mock the evaluate endpoint for smoke testing.
Returns fixed responses conforming to the sample evaluate endpoint schema.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional


class RubricCriterion(BaseModel):
    criterion_id: str
    name: str
    description: Optional[str] = None


class Rubric(BaseModel):
    rubric_id: str
    criteria: List[RubricCriterion] = []


class EvalRequest(BaseModel):
    domain: str
    prompt: str
    rubric: Rubric
    submission: str


app = FastAPI()


@app.post("/api/v1/evaluate")
def evaluate(req: EvalRequest):
    # Minimal mock response that conforms to schemas/evaluate.json
    return {
        "classification": {"label": "Human"},
        "rubric_scores": {
            "scores": [
                {"criterion_id": c.criterion_id, "name": c.name, "rating": "good"}
                for c in req.rubric.criteria
            ]
        },
        "feedback": {
            "overall_grade": "Pass",
            "reasoning": "The submission demonstrates understanding with areas to improve.",
            "criteria": [
                {
                    "criterion_id": c.criterion_id,
                    "name": c.name,
                    "rating": "good",
                    "rationale": "Solid but can be expanded",
                }
                for c in req.rubric.criteria
            ],
            "strengths": "Clear articulation of key concepts.",
            "weaknesses": "Limited exploration of counterpoints.",
            "improvement_tips": "Add references and deeper analysis in future iterations.",
        },
    }
