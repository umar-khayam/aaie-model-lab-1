"""
app/utils/parsing.py - Input validation and parsing utilities
"""

from typing import Dict, Any, List


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize criterion scores to ensure they are floats between 0 and 10.
    
    Args:
        scores: Dictionary of criterion names to scores
        
    Returns:
        Dictionary with normalized float scores
        
    Raises:
        ValueError: If any score is outside valid range [0-10]
    """
    normalized = {}
    for key, value in scores.items():
        try:
            score_float = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Score for '{key}' could not be converted to float: {value}")
        
        if not 0 <= score_float <= 10:
            raise ValueError(f"Score '{key}' must be between 0-10, got {score_float}")
        
        normalized[key] = score_float
    
    return normalized


def validate_feedback_entry(entry: Dict[str, Any]) -> bool:
    """
    Validate a feedback entry has required fields.
    
    Args:
        entry: Feedback entry dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If required fields are missing
    """
    required_fields = ['index', 'criterion_scores', 'criterion_feedback', 'feedback']
    missing = [f for f in required_fields if f not in entry]
    
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    
    return True


def truncate_text(text: str, limit: int = 200) -> str:
    """
    Truncate text to specified character limit.
    
    Args:
        text: Text to truncate
        limit: Maximum character length
        
    Returns:
        Truncated text with ellipsis if exceeded limit
    """
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def format_scores_for_display(scores: Dict[str, float]) -> str:
    """
    Format scores dictionary for display.
    
    Args:
        scores: Dictionary of criterion to score
        
    Returns:
        Formatted string representation
    """
    lines = []
    for criterion, score in scores.items():
        lines.append(f"  {criterion}: {score}/10")
    return "\n".join(lines)