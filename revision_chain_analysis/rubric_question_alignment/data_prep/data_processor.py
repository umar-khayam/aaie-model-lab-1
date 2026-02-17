import json
import re
from typing import List, Dict, Any


def chat_parser(chat_log: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract only student prompts from a raw revision chain log.
    
    Args:
        chat_log: A parsed JSON object representing a revision chain log.
                 Expected format: Contains 'revision_chain' array with 'student_prompt' fields.
        
    Returns:
        List of dictionaries with 'prompt' (str) and 'turn_index' (int) keys
        
    Behavior:
        - Iterates through revision_chain
        - Extracts only student prompts
        - Preserves step index
        - Does NOT include LLM responses
        - Does NOT modify text content
        - This function is purely structural parsing
    """
    student_prompts = []

    # Handle the data structure from revision chain logs
    # The revision chain is stored in revision_chain array with student_prompt fields
    if 'revision_chain' in chat_log:
        for step in chat_log['revision_chain']:
            if 'student_prompt' in step and step['student_prompt'].strip():
                student_prompts.append({
                    "prompt": step['student_prompt'],
                    "turn_index": step.get('step_index', 0)
                })

    return student_prompts


def extract_keywords(text: str) -> List[str]:
    """
    Normalize text into a list of keywords.
    
    Processing steps:
        1. Convert text to lowercase
        2. Remove punctuation
        3. Split into individual words
        4. Remove common stop words (optional)
    
    Args:
        text: Input text to process
        
    Returns:
        List of keywords (strings)
    """
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation (keep only letters, numbers, and spaces)
    text = re.sub(r'[^\w\s]', ' ', text)

    # Split into individual words
    words = text.split()

    # Remove common stop words (fixed - removed duplicates)
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'i', 'you', 'your', 'we', 'our', 'can',
        'or', 'but', 'not', 'this', 'have', 'had', 'his', 'her', 'she',
        'they', 'their', 'them', 'there', 'been', 'than', 'if'
    }

    # Filter words and remove duplicates
    keywords = list(dict.fromkeys([
        word for word in words 
        if word not in stop_words and len(word) > 1
    ]))

    return keywords


def load_rubric(rubric_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load rubric metadata and extract keywords from rubric text.
    
    Args:
        rubric_json: Parsed rubric JSON
        
    Returns:
        Dictionary with rubric_id, domain, and criteria (each with keywords and weight)
        
    Processing rules:
        - Extract keywords from criterion name and description
        - Use extract_keywords() for keyword extraction
        - Add weight field (float, 0-1) to each criterion
        - If rubric doesn't specify weights, use equal distribution (1/num_criteria)
        - Do NOT score or rank keywords
        - Do NOT modify rubric structure beyond keyword extraction and weight addition
    """
    processed_rubric = {
        "rubric_id": rubric_json.get("rubric_id", ""),
        "domain": rubric_json.get("domain", ""),
        "criteria": []
    }

    # Handle missing criteria gracefully
    if "criteria" in rubric_json and rubric_json["criteria"]:
        num_criteria = len(rubric_json["criteria"])
        equal_weight = 1.0 / num_criteria if num_criteria > 0 else 0.0
        
        for criterion in rubric_json["criteria"]:
            # Combine criterion name and description for keyword extraction
            text_to_process = f"{criterion.get('name', '')} {criterion.get('description', '')}"

            processed_criterion = {
                "criterion_id": criterion.get("criterion_id", ""),
                "name": criterion.get("name", ""),
                "weight": criterion.get("weight", equal_weight),
                "keywords": extract_keywords(text_to_process)
            }

            processed_rubric["criteria"].append(processed_criterion)
    else:
        # Add a default criteria entry if none exist
        processed_rubric["criteria"] = []

    return processed_rubric