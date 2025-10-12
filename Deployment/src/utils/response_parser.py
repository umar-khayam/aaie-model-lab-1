"""Helper functions for parsing LLM responses."""
import re
from typing import Tuple, Dict

def parse_classification(response: str) -> Tuple[str, float]:
    """Parse classification and confidence from LLM response.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Tuple of (classification, confidence)
    """
    classification_match = re.search(r'\*\*Classification:\*\*\s*(Human|AI Generated)', response)
    confidence_match = re.search(r'\*\*Confidence:\*\*\s*(0\.\d+|1\.0|1)', response)
    
    if not classification_match or not confidence_match:
        raise ValueError("Could not parse classification or confidence from response")
        
    return (
        classification_match.group(1),
        float(confidence_match.group(1))
    )

def parse_rubric_scores(response: str) -> Dict[str, str]:
    """Parse rubric scores from LLM response.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Dictionary of scores for each criterion
    """
    patterns = {
        'conceptual': r'\*\*Conceptual:\*\*\s*(poor|below average|average|above average|excellent)',
        'application': r'\*\*Application:\*\*\s*(poor|below average|average|above average|excellent)',
        'evaluation': r'\*\*Evaluation:\*\*\s*(poor|below average|average|above average|excellent)',
        'writing': r'\*\*Writing:\*\*\s*(poor|below average|average|above average|excellent)'
    }
    
    scores = {}
    for criterion, pattern in patterns.items():
        match = re.search(pattern, response, re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not parse {criterion} score from response")
        scores[criterion] = match.group(1).lower()
    
    return scores

def parse_feedback(response: str) -> str:
    """Parse feedback summary from LLM response.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Extracted feedback summary
    """
    match = re.search(r'\*\*Summary Feedback:\*\*\s*\n([^\n]+)', response)
    if not match:
        # If no summary section found, return the first paragraph
        paragraphs = response.split('\n\n')
        return paragraphs[0] if paragraphs else response
        
    return match.group(1).strip()
