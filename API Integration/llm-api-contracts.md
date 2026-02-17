# LLM Team API Contracts
**Author: Mohtashim Misbah (223183758)**

## 1) What this pipeline does

This FastAPI service takes a **student submission** plus a **domain‑specific prompt** and **rubric**, and returns four kinds of results that your Product UI can display:

1. **Classification** — Is the submission **AI**, **Human**, or **Hybrid**?
2. **Confidence** — A 0–1 score expressing certainty for the classification.
3. **Rubric scores** — Per‑criterion categorical ratings (Excellent/Good/Average/Needs improvement/Poor).
4. **Feedback** — Structured narrative feedback summarising strengths, weaknesses, and next steps.

Under the hood the service:
- Loads few‑shot examples by domain from `app/data/*.json`.
- Builds prompts via `app/prompting/templates.py`.
- Calls the LLM through an abstraction in `app/models/llm_client.py` (Gemini by default, Mock mode available).
- Normalises/derives outputs in `app/services/evaluator.py`.
- Surfaces four POST endpoints in `app/main.py`.

CORS is enabled for `*`, so the Product web app can call these endpoints directly from the browser.


## 2) Endpoints overview

All endpoints accept **JSON** and use the same request body (`EvalRequest`).

| Method | Path | Purpose | Response Model (intended) |
|---|---|---|---|
| POST | `/api/v1/classification` | Predict AI/Human/Hybrid + confidence | `ClassificationResponse` |
| POST | `/api/v1/confidence` | Return only the confidence value | `ConfidenceResponse` |
| POST | `/api/v1/rubric-scores` | Per‑criterion ratings | `RubricScoresResponse` |
| POST | `/api/v1/feedback` | Narrative & structured feedback | **See note on actual vs. model** |

There is also a convenience aggregator: **POST `/api/v1/evaluate`** returning `{ classification, rubric_scores, feedback }` in a single call.


## 3) Responses by endpoint

### 3.1 Classification — `POST /api/v1/classification`

What it does:
- Builds a detection prompt with few‑shots, calls the LLM for a label,
- Separately calls the confidence pathway, and
- Returns both values.

**Response**
```json
{ "label": "AI | Human | Hybrid" }
```

### 3.2 Confidence — `POST /api/v1/confidence`

What it does:
- Runs a dedicated prompt to elicit a numeric confidence estimate.

**Response**
```json
{ "confidence": 0.0 }
```


### 3.3 Rubric Scores — `POST /api/v1/rubric-scores`

What it does:
- Derives per‑criterion ratings from the **structured feedback object** (see next endpoint).

**Response**
```json
{
  "scores": [
    { "criterion_id": "C1", "name": "Clarity", "rating": "excellent|good|average|needs improvement|poor" }
  ]
}
```


### 3.4 Feedback — `POST /api/v1/feedback`

What it does:
- Prompts the LLM for a **strict JSON object** containing a narrative plus per‑criterion ratings and tips.
- Normalises paragraph fields and fills in missing ratings.

**Response**

The service returns a **structured object** like:
```json
{
  "overall_grade": "string",
  "reasoning": "string (paragraph)",
  "criteria": [
    { "criterion_id": "C1", "name": "Clarity", "rating": "excellent|good|average|needs improvement|poor", "rationale": "string (optional)" }
  ],
  "strengths": "string (paragraph)",
  "weaknesses": "string (paragraph)",
  "improvement_tips": "string (paragraph)"
}
```

## 4) Example cURL calls

```bash
# CLASSIFICATION
curl -s -X POST http://localhost:8000/api/v1/classification   -H "Content-Type: application/json"   -d @sample_request.json

# CONFIDENCE
curl -s -X POST http://localhost:8000/api/v1/confidence   -H "Content-Type: application/json"   -d @sample_request.json

# RUBRIC SCORES
curl -s -X POST http://localhost:8000/api/v1/rubric-scores   -H "Content-Type: application/json"   -d @sample_request.json

# FEEDBACK
curl -s -X POST http://localhost:8000/api/v1/feedback   -H "Content-Type: application/json"   -d @sample_request.json
```

