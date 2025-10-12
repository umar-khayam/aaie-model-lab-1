


# AAIE Model Lab - Submission Backend

This is the backend service for the AAIE Model Lab, providing a set of APIs for analyzing and evaluating text submissions. The service uses a Large Language Model (LLM) to perform tasks like classification, rubric scoring, and feedback generation.

## Features

- **FastAPI Backend**: A modern, fast (high-performance) web framework for building APIs with Python.
- **LLM Integration**: Connects to a Google GenAI model to provide intelligent text analysis.
- **Structured Logging**: Comprehensive logging for requests, responses, and errors, with daily log rotation.
- **Configuration Management**: System prompts for the LLM are managed in a separate `prompts.yaml` file.
- **Docker Support**: Comes with a `dockerfile` for easy containerization and deployment.

## API Endpoints

All endpoints are available under the `/api/v1` prefix.

### `POST /api/v1/classify`

Analyzes a text submission to determine if it was written by a human or an AI.

- **Request Body**:
  ```json
  {
    "text": "The text to be classified.",
    "metadata": { "key": "value" }
  }
  ```
- **Response Body**:
  ```json
  {
    "classification": "Human",
    "confidence": 0.85
  }
  ```

### `POST /api/v1/rubric-score`

Scores a text submission based on a predefined rubric.

- **Request Body**: (Same as `/classify`)
- **Response Body**:
  ```json
  {
    "conceptual": "average",
    "application": "above average",
    "evaluation": "average",
    "writing": "excellent"
  }
  ```

### `POST /api/v1/generate-feedback`

Generates constructive feedback for a text submission.

- **Request Body**: (Same as `/classify`)
- **Response Body**:
  ```json
  {
    "feedback": "This is a well-written submission..."
  }
  ```

### `POST /api/v1/evaluate`

Performs a comprehensive evaluation of a submission, combining classification, rubric scoring, and feedback.

- **Request Body**: (Same as `/classify`)
- **Response Body**:
  ```json
  {
    "classification": {
      "classification": "Human",
      "confidence": 0.85
    },
    "rubric_scores": {
      "conceptual": "average",
      "application": "above average",
      "evaluation": "average",
      "writing": "excellent"
    },
    "ai_feedback": "This is a well-written submission..."
  }
  ```

### `GET /api/v1/llm-status`

Checks the status of the connected LLM and returns metadata about the model.

## Local Development

### Prerequisites

- Python 3.11+
- Pip

### Setup

1.  **Clone the repository** and navigate to the `Deployment` directory.

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**:
    Create a `.env` file in the `Deployment` directory and add your Google API key and Model ID:
    ```
    GOOGLE_API_KEY="your_api_key"
    GOOGLE_MODEL_ID="gemini-2.0-flash" 
    ```

### Running the Application

To run the application with live reloading:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Configuration

The system prompts used to guide the LLM's responses are located in `src/config/prompts.yaml`. You can modify these prompts to change the behavior of the different endpoints without changing any code.

## Docker

### Building the Image

To build the Docker image for this service:

```bash
docker build -t innovaite.aaie.model-lab/submission-backend:latest .
```

### Running the Container

#### Local Development

For local development, you can use an `.env` file to manage your environment variables.

```bash
docker run -p 8000:8000 --env-file .env innovaite.aaie.model-lab/submission-backend
```

Make sure your `.env` file is present in the `Deployment` directory when running this command. The API will be accessible on `http://localhost:8000`.

#### Production

For production, it's recommended to pass environment variables directly to the `docker run` command or use a secret management system.

```bash
docker run -p 8000:8000 -e GOOGLE_MODEL_ID="gemini-2.0-flash" -e GOOGLE_API_KEY="your_api_key" innovaite.aaie.model-lab/submission-backend
```
