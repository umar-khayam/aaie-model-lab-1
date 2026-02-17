# Educator Feedback Quality API

This service exposes a FastAPI-based API that evaluates educator feedback quality using DeepEval’s G-Eval metric with the `gpt-4o` model.

---

## Prerequisites

- Python 3.10+ installed on your system   
- An OpenAI API key available as an environment variable `OPENAI_API_KEY` (required by DeepEval / G‑Eval) 

---

## 1. Clone and enter the project

```powershell
git clone this repo
cd G-eval-API
```

---

## 2. Create and activate a virtual environment

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

You should now see `(.venv)` in your PowerShell prompt, indicating the environment is active.

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

This installs:

- **fastapi** – web framework for the API   
- **uvicorn** – ASGI server used to run the app   
- **deepeval** – framework providing the G‑Eval metric and LLM-as-a-judge evaluation   

---

## 4. Configure environment variables

Create a `.env` file in the project root (same folder as `app/`) and add:

OPENAI_API_KEY="your_openai_api_key_here"


`python-dotenv` will load these values so DeepEval and the OpenAI client can authenticate correctly.


## 5. Run the API locally

From the project root (with the venv still active):

```powershell
uvicorn app.main:app --reload --port 8000
```

- `app.main:app` points to the FastAPI app instance inside `app/main.py`.  
- `--reload` enables auto-reload on code changes (recommended for development).  

Once started, you should see log lines similar to:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Waiting for application startup.
2026-01-19 ... - app.main - INFO - Starting Educator Feedback Quality API...
INFO:     Application startup complete.
```

---

## 6. Explore the API docs

With the server running, open:

- Interactive Swagger UI: `http://127.0.0.1:8000/docs` 
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json` 
The FastAPI docs UI lets you inspect endpoints and send test requests directly from the browser.

---

## 7. Health check endpoints

To confirm the service is healthy, you can call:

- Root health: `GET http://127.0.0.1:8000/health`  
- Feedback service health: `GET http://127.0.0.1:8000/api/v1/feedback/health`  

Successful requests return HTTP 200 and corresponding log entries like:

```text
2026-01-19 ... - app.api.feedback - INFO - Health check requested
INFO:     127.0.0.1:61538 - "GET /api/v1/feedback/health HTTP/1.1" 200 OK
```

These are handy for monitoring and for automated readiness checks .

---

## 8. Evaluate feedback

The main endpoint accepts one or more feedback entries and returns a quality score (0–1) using DeepEval’s Educator Feedback Quality G‑Eval metric.

Example request (via Swagger UI or a REST client):

- **Method:** `POST`  
- **URL:** `http://127.0.0.1:8000/api/v1/feedback/evaluate-feedback`  

Example JSON body:

```json
{
  "data": [
    {
    "index": 1,
    "quality": null,
    "authorship": null,
    "criterion_scores": {
      "Conceptual Understanding": 10,
      "Application to Real-World Scenarios": 9,
      "Critical Evaluation": 10,
      "Structure and Academic Writing": 10
    },
    "criterion_feedback": {
      "Conceptual Understanding": "The student's prompts show a comprehensive grasp of MFA, its components, and its role in cybersecurity, demonstrating deep theoretical understanding.",
      "Application to Real-World Scenarios": "The student effectively prompts for comparisons of MFA methods and their integration into strategies, indicating a strong ability to apply concepts to practical scenarios.",
      "Critical Evaluation": "The student consistently pushes for an analysis of trade-offs, limitations, and evolving attack vectors, showcasing excellent critical thinking and evaluation skills.",
      "Structure and Academic Writing": "The student's prompts are clear, well-articulated, and directly address the assignment's requirements, indicating strong organizational and communication skills."
    },
    "weighted_score_percent": 98.0,
    "feedback": "EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS\nThe student demonstrates a strong learning process by actively seeking to understand the nuances of MFA, as evidenced by their detailed prompts exploring various methods, their trade-offs, and integration into broader strategies. The engagement level is high, consistently probing for deeper insights. To further enhance their learning, the student could explore specific case studies of data breaches where MFA was either effective or bypassed, and investigate the evolving landscape of MFA bypass techniques and countermeasures. This would deepen their critical evaluation and real-world application.\n\nRUBRIC SCORES\nConceptual Understanding: 10/10 - The student's prompts show a comprehensive grasp of MFA, its components, and its role in cybersecurity, demonstrating deep theoretical understanding.\nApplication to Real-World Scenarios: 9/10 - The student effectively prompts for comparisons of MFA methods and their integration into strategies, indicating a strong ability to apply concepts to practical scenarios.\nCritical Evaluation: 10/10 - The student consistently pushes for an analysis of trade-offs, limitations, and evolving attack vectors, showcasing excellent critical thinking and evaluation skills.\nStructure and Academic Writing: 10/10 - The student's prompts are clear, well-articulated, and directly address the assignment's requirements, indicating strong organizational and communication skills."
  }
  ],
  "model": "gpt-4o"
}
```

On success, logs will show something like:

```text
2026-01-19 ... - app.api.feedback - INFO - Received request with 1 feedback entries
2026-01-19 ... - app.services.feedback_generator - INFO - FeedbackQualityEvaluator initialized with model: gpt-4o
2026-01-19 ... - app.services.feedback_generator - INFO - Entry 1 evaluated with score: 0.9060...
2026-01-19 ... - app.api.feedback - INFO - Evaluation complete. Mean score: 0.91
```

The response payload includes per‑entry scores and an overall mean score, which you can aggregate or surface in your frontend or analysis pipeline.

---

## 9. Stopping the server

To stop the development server, go to the terminal where `uvicorn` is running and press:

```text
CTRL + C
```

The process will terminate and free up port 8000 for the next run.
