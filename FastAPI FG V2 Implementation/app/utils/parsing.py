import re

# Regex pattern to extract criterion scores and feedback
score_with_text_pattern = re.compile(
    r"^(.*?):\s*(10|[0-9])\s*/\s*10\s*-\s*(.*)$",
    re.MULTILINE
)

def output_incomplete(text: str) -> bool:
    patterns = [
        r"\[.*?sentence.*?\]",
        r"→ .*?:\s*\[",
        r"Write a \d–\d sentence",
        r"\[\d–\d\]"
    ]
    return any(re.search(p, text) for p in patterns)

def extract_scores_and_feedback(feedback_text: str):
    scores = {}
    feedback = {}
    for match in score_with_text_pattern.finditer(feedback_text):
        name = match.group(1).strip()
        score = int(match.group(2))
        explanation = match.group(3).strip()
        scores[name] = score
        feedback[name] = explanation
    return scores, feedback

def compute_weighted_score(rubric: dict, scores_by_name: dict) -> float:
    total_weight = 0.0
    weighted_sum = 0.0
    for c in rubric.get("criteria", []):
        name = c.get("name")
        weight = float(c.get("weight", 0))
        if name in scores_by_name:
            weighted_sum += (scores_by_name[name] / 10.0) * weight
            total_weight += weight
    return round((weighted_sum / total_weight) * 100, 1) if total_weight else 0.0
