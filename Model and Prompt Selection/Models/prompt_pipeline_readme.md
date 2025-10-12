# Prompt Pipeline

This document outlines the process for running the `prompt-pipeline.py` script, which processes student submissions to detect AI-generated content and provide feedback.

## Prerequisites

- Python 3.8 or higher
- An environment that can run PyTorch (e.g., a local machine with a GPU, or a cloud-based environment)

## Installation

1.  **Install Dependencies:**
    Install the required Python packages using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create a `.env` file:**
    In the same directory as the script, create a file named `.env`.

2.  **Set Environment Variables:**
    Add the following variables to your `.env` file:

    ```
    MODEL_ID="your-hugging-face-model-id"
    HF_TOKEN="your-hugging-face-api-token"
    ```

    - `MODEL_ID`: The identifier of the Hugging Face model you want to use (e.g., `meta-llama/Llama-2-7b-chat-hf`).
    - `HF_TOKEN`: Your Hugging Face API token for authentication.

## Running the Script

Execute the script from your terminal:

```bash
python prompt-pipeline.py
```

The script will perform the following actions:
- Initialize the specified model and tokenizer.
- Process each JSON file in the `Training Data` directory.
- For each submission, it will generate:
  - An AI-detection analysis.
  - Structured feedback based on the provided rubric.
- Log all operations to the console and a log file.

## Output

The script generates two main output files:

1.  **`prompt_pipeline_output.md`**:
    A markdown file containing the formatted outputs from the model for each submission. This includes the AI detection results and the generated feedback.

2.  **`prompt_pipeline.log`**:
    A log file that records detailed information about the script's execution, including timestamps, informational messages, and any errors that occurred. This is useful for debugging and tracking the pipeline's performance.
