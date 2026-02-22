# AI Feedback Generator API

This service exposes a FastAPI-based API that generates educator-style feedback and rubric-aligned scores for student submissions using Google Gemini (`gemini-2.5-flash`).

***

## Prerequisites

- Python 3.10+ installed on your system   
- A Google Gemini API key available as an environment variable `API_KEY` (required for model access) 

***

## 1. Clone and enter the project

```powershell
git clone this repo
cd FastAPI FG V2 Implementation
```

***

## 2. Create and activate a virtual environment

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

You should now see `(.venv)` in your PowerShell prompt, indicating the environment is active. 

***

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

This installs:

- **fastapi** – web framework for the API   
- **uvicorn** – ASGI server used to run the app   
- **pydantic** – data validation and settings management   
- **google-genai** – Google Gemini model client   
- **python-dotenv** – loads environment variables from `.env`.

***

## 4. Configure environment variables

Create a `.env` file in the project root (same folder as `main.py`) and add:

```
API_KEY="your_google_gemini_api_key_here"
GEMINI_MODEL="gemini-2.5-flash"
```

`python-dotenv` will load these values so the Gemini client can authenticate correctly.

***

## 5. Run the API locally

From the project root (with the venv still active):

```powershell
uvicorn main:app --reload --port 8000
```


- `main:app` points to the FastAPI app instance inside `main.py`.  
- `--reload` enables auto-reload on code changes (recommended for development).  

Once started, you should see log lines similar to:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

***

## 6. Explore the API docs

With the server running, open:

- Interactive Swagger UI: `http://127.0.0.1:8000/docs` 
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json` 
The FastAPI docs UI lets you inspect endpoints and send test requests directly from the browser. 
***

## 7. Health check endpoints

To confirm the service is healthy, you can call:

- Root health: `GET http://127.0.0.1:8000/` 

Successful requests return HTTP 200 and the message:

```json
{"message": "FastAPI Feedback Generator v2 is running."}
```


These are handy for monitoring and for automated readiness checks.

***

## 8. Generate feedback

The main endpoint accepts an assignment domain, prompt, rubric, and one or more submissions, returning structured educator feedback and scores.

Example request (via Swagger UI or a REST client):

- **Method:** `POST`  
- **URL:** `http://127.0.0.1:8000/api/v2/generate-feedback`

Example JSON body:

```json
{
  "domain": "Higher Education",
  "prompt": "Write a 500-word reflection on AI ethics.",
  "rubric": {
    "rubric_id": "rubric-1",
    "criteria": [
      {
        "criterion_id": "c1",
        "name": "Clarity",
        "description": "How clear and well-structured the response is.",
        "performance_descriptors": {
          "excellent": "Exceptionally clear.",
          "good": "Mostly clear.",
          "average": "Adequately clear.",
          "needs_improvement": "Somewhat unclear.",
          "poor": "Very unclear."
        },
        "weight": 30
      }
    ]
  },
  "submissions": [
    {
      "final_submission": "Student response text goes here...",
      "quality": "medium",
      "authorship": "human"
    }
  ]
}
```


On success, logs will show Gemini API calls and parsing, and the response includes:

```json
[
  {
    "index": 1,
    "quality": "medium",
    "authorship": "human",
    "criterion_scores": {
      "Clarity": 8
    },
    "criterion_feedback": {
      "Clarity": "Clear structure with minor gaps."
    },
    "weighted_score_percent": 80.0,
    "feedback": "EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS\nStrengths include solid grasp of core concepts. Improve by adding examples. Next steps: Expand on implications.\n\nRUBRIC SCORES\nClarity: 8/10 - Clear structure with minor gaps."
  }
]
```


The service:

- Builds domain-specific prompts for Gemini. 
- Parses structured scores/explanations from model output. 
- Computes weighted overall score based on rubric weights.
***

## 9. Stopping the server

To stop the development server, go to the terminal where `uvicorn` is running and press:

```text
CTRL + C
```

The process will terminate and free up port 8000 for the next run. 