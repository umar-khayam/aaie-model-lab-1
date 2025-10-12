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
        Rating: Excellent | Good | Average | Needs Improvement | Poor
        Reason:
        - point 1
        - point 2
        Improvement Tip: one concrete suggestion

        Overall Rating: Excellent | Good | Average | Needs Improvement | Poor
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
3) Overall Rating: Excellent | Good | Average | Needs Improvement | Poor

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
