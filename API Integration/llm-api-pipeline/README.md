# LLM Evaluation Pipeline (FastAPI)

A production-ready FastAPI service that ingests assignment submissions and returns:
- **Classification** (e.g., AI / Human / Hybrid)
- **Confidence** of the classification (0–1)
- **Rubric scores** per criterion with rationales
- **Overall feedback** (strengths, weaknesses, next steps)

It supports **few-shot priming by domain** using your JSON datasets and is wired for **Gemini** by default, with a clean provider interface. A **mock mode** is available to run without any API keys.

## Quick Start

### 1) Python env
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Data
Place your domain JSON files in `./data/` (or set `DATA_DIR`). You can copy the provided samples if running in this environment:
- `accounting.json`
- `engineering.json`
- `it.json`
- `psychology.json`
- `teaching.json`

The loader expects each JSON to have the shape:
```json
{
  "domain": "Accounting",
  "prompt": "...",
  "rubric": {
    "rubric_id": "rub_...",
    "criteria": [ { "criterion_id": "...", "name": "...", "description": "...", "performance_descriptors": { ... } } ]
  },
  "submissions": [ { "final_submission": "...", "label_type": "AI|Human|Hybrid" }, ... ]
}
```

### 3) Configure
Create a `.env` from the example and set your keys:
```bash
cp .env.example .env
# edit .env
```

### 4) Run
```bash
uvicorn app.main:app --reload --port 8000
```

Open docs at: http://localhost:8000/docs

### 5) Mock mode (no keys required)
Set `MOCK=1` in `.env` to bypass real LLM calls and return deterministic sample outputs.
Useful for frontend integration and CI.

---

## API Overview

All endpoints accept the **same input**:
```json
{
  "domain": "Accounting",
  "prompt": "...",
  "rubric": { "rubric_id": "...", "criteria": [ ... ] },
  "submission": "...",
  "actual_label": "AI|Human|Hybrid"
}
```
If you prefer, you can just send `domain`, `prompt`, `rubric`, `submission` and omit `actual_label`.

**Endpoints:**
- `POST /api/v1/classification` → `{ "label": "AI|Human|Hybrid", "rationale": "..." }`
- `POST /api/v1/confidence` → `{ "confidence": 0.83, "basis": "..." }`
- `POST /api/v1/rubric-scores` → `{ "scores": [ { "criterion_id": "...", "name": "...", "score": 0.0-1.0, "rationale": "..." } ], "overall": 0.0-1.0 }`
- `POST /api/v1/feedback` → `{ "feedback": { "strengths": [...], "weaknesses": [...], "next_steps": [...] } }`
- `POST /api/v1/evaluate` → merges the four responses into one object

All outputs are **strict JSON**, validated via Pydantic models.

---

## Few-shot selection
Given an incoming `domain`, the service loads the corresponding domain JSON (e.g., `accounting.json`) and picks a small set of examples from `submissions` to include as in-context few-shots. Strategies:
- Balanced sampling across label types (AI / Human / Hybrid) if available.
- Cap the total few-shots via `FEWSHOT_MAX` (default 6).
- Deterministic selection (hash + round-robin) for reproducibility.

---

## Provider interface
`LLMClient` is an abstract base. The default `GeminiClient` calls the Gemini API (text generation). You can add more providers easily (e.g., OpenAI, DeepSeek) by conforming to the same interface.

Environment variables:
- `PROVIDER=gemini|mock` (derived automatically from `MOCK`)
- `GEMINI_API_KEY` (if `MOCK!=1`)
- `GEMINI_MODEL` (default: `gemini-1.5-pro`)
- `TEMPERATURE` (default: 0.2)
- `MAX_OUTPUT_TOKENS` (default: 1024)

---

## Testing
```bash
pytest -q
```

---

## Docker (later)
This repo is structured to be Docker-friendly. You can add a `Dockerfile` and use `ENV` variables or secrets at deploy time.
