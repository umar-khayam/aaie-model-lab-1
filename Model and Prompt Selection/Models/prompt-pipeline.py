from datetime import datetime
from huggingface_hub import login
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    logging,
    pipeline
)
import torch
from dotenv import load_dotenv
import json
import os
import time
import logging
import sys
import glob
import re
import platform
from pathlib import Path
from typing import List, Dict, Any


# Configure logging
def setup_logging() -> logging.Logger:
    """
    Initializes and configures the logging system with both console and file handlers.
    
    Returns:
        logging.Logger: Configured logger instance with both console (INFO level) and 
                       file (DEBUG level) handlers set up.
    """
    # Clear any existing handlers to avoid duplicates
    logging.root.handlers = []
    
    logger = logging.getLogger('prompt_pipeline')
    logger.handlers = []  # Clear any existing handlers
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent duplicate logging
    
    # Create console handler with INFO level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create file handler for DEBUG and above
    file_handler = logging.FileHandler('prompt_pipeline.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    
    # Create a single format for both console and file
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)
    
    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Add a startup message to confirm logging is working
    logger.info("Logging system initialized")
    logger.debug("Debug logging enabled (check prompt_pipeline.log for detailed logs)")
    
    return logger

# Set up the logger
logger = setup_logging()

# Define system prompts and base user prompts
SYSTEM_PROMPT = "You are a careful academic assistant. Be precise and give clear structured output (not JSON, not CSV, no files)."

def build_detection_prompt(submission: str, few_shots: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Academic Integrity Detector Prompt
    ----------------------------------
    Purpose:
        Classifies student submissions as Human, AI, or Hybrid (AI-assisted).

    Technique:
        - Role-based prompting
        - Few-shot support
        - CoT (reasoning encouraged but hidden from output)
        - Output in plain text 

    Expected Output (example format in plain text):
        Label: Human | AI | Hybrid
        Rationale:
        - short bullet point 1
        - short bullet point 2
        Flags: style_inconsistency / high_verbatim / generic_phrasing / none
    """
    # Build few-shot block
    shot_texts = []
    for s in few_shots:
        shot_texts.append(
            f'Submission: """{s.get("final_submission","")}"""\n'
            f'Your analysis (2–4 bullet points): <analysis>\n'
            f'Label: {s.get("label_type","")}\n'
        )
    examples_block = "\n\n".join(shot_texts) if shot_texts else "/* no examples available */"

    user = f"""
You are an AI text-source classifier for academic integrity.
Decide whether the student submission is Human, AI, or Hybrid (AI-assisted).

Guidelines:
- Consider discourse features (specificity, subjectivity, personal context), style consistency, local/global coherence, repetitiveness, and cliché patterns.
- Hybrid = meaningful human writing with some AI assistance, or explicit admission of mixed use.

Examples:
{examples_block}

Now analyze the NEW submission and respond in plain text with the following structure:
Label: ...
Rationale:
- point 1
- point 2
Flags: ...
NEW submission:
\"\"\"{submission}\"\"\"\n
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_feedback_prompt(domain: str, assignment_prompt: str, rubric_text: str, submission: str) -> List[Dict[str, str]]:
    """
    Rubric-Aligned Feedback Prompt
    ------------------------------
    Purpose:
        Generates structured, supportive feedback for a student submission.

    Technique:
        - Role-based prompting
        - Rubric-grounded evaluation
        - Output in plain text 

    Expected Output (example format in plain text):
        Overall Summary:
        <2–4 sentence overview>

        Criteria Feedback:
        Criterion: <criterion_id>
        Rating: excellent | good | average | needs_improvement | poor
        Evidence:
        - point 1
        - point 2
        Improvement Tip: one concrete suggestion

        Suggested Grade: <optional short string>
    """
    user = f"""
You are a supportive assessor. Provide actionable feedback aligned to the rubric.
Return plain structured text only (no JSON, no files).

Sections to include:
1) Overall Summary: 2–4 sentences on strengths and priorities.
2) Criteria Feedback: for each rubric criterion include:
   - Criterion
   - Rating (excellent, good, average, needs_improvement, poor)
   - Evidence (1–3 bullet points citing excerpts or behaviors)
   - Improvement Tip (one concrete step)
3) Suggested Grade: short string (optional)

Context:
- Domain: {domain}
- Assignment prompt: {assignment_prompt}

Rubric (verbatim):
{rubric_text}

Student submission:
\"\"\"{submission}\"\"\"\n
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


# Functions for getting all JSON files from Training Data folder
def get_training_data_files() -> tuple[List[str], List[str]]:
    """
    Retrieves all JSON files from the Training Data folder in the current directory.
    
    Returns:
        tuple[List[str], List[str]]: A tuple containing:
            - paths (List[str]): Absolute paths to all JSON files in the Training Data directory
            - filenames (List[str]): Names of all JSON files (without path)
    
    Notes:
        Searches for JSON files in the "Training Data" subdirectory relative to the
        current script's location. Logs the number of files found.
    """
    current_dir = Path(__file__).parent
    training_data_dir = current_dir / "Training Data"
    paths = glob.glob(str(training_data_dir / "*.json"))
    filenames = [Path(p).name for p in paths]
    logger.info(f"Found {len(paths)} JSON files in Training Data directory")
    return paths, filenames


def load_rubric_from_json(json_path: str) -> Dict[str, Any]:
    """
    Loads and parses a rubric from a JSON file.
    
    Args:
        json_path (str): Path to the JSON file containing the rubric data.
    
    Returns:
        Dict[str, Any]: The parsed rubric data structure.
        
    Raises:
        UnicodeDecodeError: If the file is not properly UTF-8 encoded.
        json.JSONDecodeError: If the file contains invalid JSON.
        Exception: For other unexpected errors during file operations.
    """
    logger.debug(f"Loading rubric from {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            rubric = json.load(f)
        logger.debug("Rubric loaded successfully")
        return rubric
    except UnicodeDecodeError as e:
        logger.error(f"Error loading rubric from {json_path}: Unicode decode error. Try saving the file with UTF-8 encoding.")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error loading rubric from {json_path}: Invalid JSON format")
        raise
    except Exception as e:
        logger.error(f"Error loading rubric from {json_path}: {str(e)}")
        raise


def format_rubric(rubric: Dict[str, Any]) -> str:
    """
    Formats a rubric dictionary into a human-readable string format.
    
    Args:
        rubric (Dict[str, Any]): The rubric data structure containing 'rubric_id',
            'criteria', and nested performance descriptors.
    
    Returns:
        str: A formatted string representation of the rubric with hierarchical structure,
            including criteria descriptions and performance descriptors.
    """
    formatted_rubric = f"""
    Rubric ID: {rubric['rubric_id']}

    Criteria:
    """

    for rubric_item in rubric['criteria']:
        formatted_rubric += f"""
        Criterion: {rubric_item['criterion_id']}
        Name: {rubric_item['name']}
        Description: {rubric_item['description']}
        Performance Descriptors:
        """
        for key, val in rubric_item['performance_descriptors'].items():
            formatted_rubric += f"""
            - {key}: {val}
            """
    return formatted_rubric


# Function to write output to md file
def write_output_to_md(file_path: str, content: str) -> None:
    """
    Writes content to a markdown file, creating or overwriting the file.
    
    Args:
        file_path (str): Path to the output markdown file.
        content (str): Content to write to the file.
    
    Raises:
        PermissionError: If the process lacks permission to write to the file.
        IOError: If there are issues during file writing operations.
        Exception: For other unexpected errors during file operations.
        
    Notes:
        - Uses fsync to ensure content is written to physical storage
        - Verifies file existence and content after writing
        - Logs success or failure of the operation
    """
    try:
        # Check if file exists first
        if Path(file_path).exists():
            logger.info(f"File {file_path} already exists - overwriting")
            
        # Write the new content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()  # Ensure content is written to disk
            os.fsync(f.fileno())  # Force write to physical storage
            
        # Verify the file was written
        if Path(file_path).exists() and Path(file_path).stat().st_size > 0:
            logger.info(f"Successfully wrote output to {file_path}")
        else:
            logger.error(f"Failed to write content to {file_path}")
            
    except PermissionError:
        logger.error(f"Permission denied when trying to write to {file_path}")
        raise
    except IOError as e:
        logger.error(f"IO Error when writing to {file_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when writing to {file_path}: {str(e)}")
        raise


# Functions for model processing
def process_prompt(hf: Any, prompt: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Processes a prompt through the model pipeline and measures execution time.
    
    Args:
        hf (Any): The initialized Hugging Face pipeline object for text generation.
        prompt (List[Dict[str, str]]): The formatted prompt messages to send to the model.
    
    Returns:
        List[Dict[str, Any]]: The model's response containing generated text.
    """
    t1 = time.time()
    response = hf(prompt)
    t2 = time.time()
    logger.info(f"Model response: {response}")
    logger.info(f"Time taken for model inference: {t2-t1:.2f} seconds")
    return response


def extract_assistant_answer(response: List[Dict[str, Any]]) -> tuple[str | None, str | None]:
    """
    Extracts the assistant's response and thinking process from the model output.
    
    Args:
        response (List[Dict[str, Any]]): The raw response from the model pipeline.
    
    Returns:
        tuple[str | None, str | None]: A tuple containing:
            - answer (str | None): The main response content with think blocks removed
            - thinking (str | None): The extracted content from think blocks, if any
    """
    if not response:
        return None
    generated_text = response[0]['generated_text'] if response else ""
    assistant_message = [item['content'] for item in generated_text if item.get('role') == 'assistant']
    
    if not assistant_message:
        return None, None
    
    think_pattern = r'<think>(.*?)</think>'
    
    # Extract thinking content
    think_matches = re.findall(think_pattern, assistant_message[0], re.DOTALL)
    thinking = '\n'.join(think_matches) if think_matches else None
    
    # Remove think blocks from main answer
    answer = re.sub(think_pattern, '', assistant_message[0], flags=re.DOTALL)
    answer = answer.strip()

    logger.info(f"Answer: {answer}")
    logger.info(f"Thinking process: {thinking}")
    return answer, thinking


def initialise_model() -> tuple[Any, str]:
    """
    Initializes the language model and tokenizer using environment variables.
    
    Returns:
        tuple[Any, str]: A tuple containing:
            - hf (Any): The initialized Hugging Face pipeline for text generation
            - model_id (str): The identifier of the loaded model
    
    Notes:
        Requires environment variables:
            - MODEL_ID: The Hugging Face model identifier
            - HF_TOKEN: Authentication token for Hugging Face Hub
            
        Uses local cache directory '.cache/huggingface' for model storage.
    """
    logger.info("Loading environment variables and initializing model")
    load_dotenv()

    model_id = os.getenv("MODEL_ID")
    if not model_id:
        logger.error("MODEL_ID not found in environment variables")
        return

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        logger.error("HF_TOKEN not found in environment variables")
        return
    login(hf_token)
    
    logger.info(f"Initializing model: {model_id}")
    # load model and tokenizer to specified cache in local project folder
    model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir=".cache/huggingface", token=hf_token)
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=".cache/huggingface", token=hf_token)

    local_path = model_id
    hf = pipeline("text-generation", model=local_path, tokenizer=tokenizer, temperature=0.7, max_new_tokens=1024)
    logger.info("Model initialization completed")
    return hf, model_id


def main():
    try:
        start_time = time.time()
        hf, model_id = initialise_model()

        paths, filenames = get_training_data_files()
        if not paths:
            logger.error("No rubric files found")
            return

        run_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output_md = "# Prompt Pipeline Output\n\n"
        output_md += f"Model: {model_id}\n\n"
        output_md += f"Date: {run_datetime}\n\n"

        output_md += "### System Information\n\n"
        output_md += f"* Machine: {platform.machine()}\n"
        output_md += f"* Version: {platform.version()}\n"
        output_md += f"* Platform: {platform.platform()}\n"
        output_md += f"* Uname: {platform.uname()}\n"
        output_md += f"* System: {platform.system()}\n"
        output_md += f"* Processor: {platform.processor()}\n\n"


        for path, filename in zip(paths, filenames):

            output_md += f"## Processing File: {filename}\n\n"
            rubric = load_rubric_from_json(path)

            for i in range(len(rubric['submissions'])):
                submission_text = rubric['submissions'][i]['final_submission']
                submission_label = rubric['submissions'][i]['label_type']

                logger.info(f"Building detection prompt for submission {i} in {filename}")
                detection_messages = build_detection_prompt(submission_text, [])  # Empty list for few_shots for now

                logger.info(f"Processing detection prompt for submission {i} in {filename}")
                detection_response = process_prompt(hf, detection_messages)
                detection_answer, detection_thinking = extract_assistant_answer(detection_response)

                output_md += f"### Results for submission {i} in {filename}\n\n"
                output_md += f"**Detection Answer for submission {i} in {filename}**\n\n"
                output_md += f"```\n{detection_answer}\n```\n\n"
                output_md += f"Expected Label: {submission_label}\n\n"
                output_md += f"**Detection Thinking for submission {i} in {filename}**\n\n"
                output_md += f"```\n{detection_thinking}\n```\n\n"

                logger.info(f"Building feedback prompt for submission {i} in {filename}")
                feedback_messages = build_feedback_prompt(
                    domain=rubric['domain'],
                    assignment_prompt=rubric['prompt'],
                    rubric_text=format_rubric(rubric['rubric']),
                    submission=submission_text
                )

                logger.info(f"Processing feedback prompt for submission {i} in {filename}")
                feedback_response = process_prompt(hf, feedback_messages)
                feedback_answer, feedback_thinking = extract_assistant_answer(feedback_response)

                output_md += f"**Feedback Answer for submission {i} in {filename}**\n\n"
                output_md += f"```\n{feedback_answer}\n```\n\n"
                output_md += f"**Feedback Thinking for submission {i} in {filename}**\n\n"
                output_md += f"```\n{feedback_thinking}\n```\n\n"

                end_time = time.time()
        total_time = end_time - start_time
        minutes = int(total_time // 60)
        seconds = total_time % 60
        logger.info(f"Total processing time: {minutes}:{seconds:.2f} minutes")
        output_md += f"## Total processing time: {minutes}:{seconds:.2f} minutes\n"

        # Write the complete output to a markdown file
        write_output_to_md("prompt_pipeline_output.md", output_md)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    main()
