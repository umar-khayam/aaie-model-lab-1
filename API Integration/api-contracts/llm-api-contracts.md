# LLM Team API Contracts
**Author: Mohtashim Misbah (223183758)**

## 1) What this pipeline does - Version 1

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


## 2) Endpoints overview - Version 1

All endpoints accept **JSON** and use the same request body (`EvalRequest`).

| Method | Path | Purpose | Response Model (intended) |
|---|---|---|---|
| POST | `/api/v1/classification` | Predict AI/Human/Hybrid + confidence | `ClassificationResponse` |
| POST | `/api/v1/confidence` | Return only the confidence value | `ConfidenceResponse` |
| POST | `/api/v1/rubric-scores` | Per‑criterion ratings | `RubricScoresResponse` |
| POST | `/api/v1/feedback` | Narrative & structured feedback | **See note on actual vs. model** |

There is also a convenience aggregator: **POST `/api/v1/evaluate`** returning `{ classification, rubric_scores, feedback }` in a single call.


## 3) Responses by endpoint - Version 1

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

## 4) Example cURL calls - Version 1

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

## 5) Version 2 (OpenAPI)

For Version 2, the API Contract is defined using OpenAPI specification and includes two required endpoints for T32025 MVP:
- Submission evaluation grading and feedback generation (`v2/evaluate`)
- Revision chain log profiling (`v2/rc_profile`)

The spec is available at:
- `API Integration/api-contracts/llm-v2.openapi.yml`

Benefits of using OpenAPI spec instead of markdown format:
- Consolidated evaluation endpoint patterns under `/api/v2` with clearer request/response contracts designed for stricter typing and better client generation.
- OpenAPI-first design: the v2 spec is intended to be the single source of truth for client SDK generation and contract tests.
- Schemas can be directly referenced in spec file if desired.
- Can be quickly reviewed by rendering using online editor such as `https://editor.swagger.io/` or local cli (see `Quick usage`)
- TypeScript clients can be generated from OpenAPI spec using tools such as `Hey API` (node.js) and `Orval` (React).

Backward compatibility:
- v1 endpoints should be remained available while v2 is in development.

### Quick usage
1. Create venv:

```cli
python -m venv openapi-venv
openapi-venv\Scripts\activate.bat
```

2. Render interactive docs for reviewing (example using `mkdocs`):

Install `mkdocs`:
```cli
pip install mkdocs mkdocs-render-swagger-plugin
```

Create below folder structure:
docs/
  ├── index.md
  ├── llm-v2.openapi.md
  └── llm-v2.openapi.yml
mkdocs.yml

Template for mkdocs.yml

```
site_name: API Contracts
plugins:
  - render_swagger:
        allow_arbitrary_locations: true

nav:
  - Home: index.md
  - API Reference: llm-v2.openapi.md
```

Template for index.md

```
# Welcome to API Docs
```

Template for llm-v2.openapi.md

```
# API Reference

!!swagger llm-v2.openapi.yml!!
```

Serve the docs

```cli
mkdocs serve
```

### Data flow (high level)
- Client (e.g., Product Backend) -> HTTP POST `/api/v2/evaluate` with structured JSON.
- FastAPI service receives request, validates against v2 schema as per the reference.
- Service constructs prompts using `app/prompting/templates.py` (require updates for v2 shapes).
- `app/models/llm_client.py` invokes the LLM (Gemini or mock) and returns raw text/JSON.
- Post-processing layer (`app/services/evaluator.py`) normalises LLM outputs into the v2 response schema, attaches `model_metadata`, and optionally stores traces/audit records.
- Response returned to client (e.g., Product Backend); async telemetry and explainability artifacts can be persisted to storage (e.g, MongoDB).

### Recommended future versioning strategy
- API Versioning
  - Major versions (v1, v2, v3) signal breaking changes to request/response contracts.
  - Minor/patching: use semantic versioning for the service and schema files (e.g., `1.2.0`), where minor increments can add optional fields while preserving backwards compatibility.

- OpenAPI and Schema Management
  - Keep OpenAPI spec as the canonical source of truth; generate SDKs and contract tests from it.
  - Store spec under `api-contracts/` and tag commits that change the contract.
  - Use automated contract tests in CI that validate server responses against the spec.

- Prompt/Manifest Versioning
  - Separate prompt manifest versioning (e.g., `edu.feedback.v1`) from API versions; allow prompt change without bumping API major version when the contract remains compatible.
  - Promote `status` changes (`dev` -> `staging` -> `production`) via CI gates.

