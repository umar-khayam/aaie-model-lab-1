"""Prompt construction utilities for LLM evaluation.

This module contains helper functions to build prompts used by the
evaluation service. It exposes legacy functions that are still used
for certain tasks (e.g. confidence and rubric scoring) as well as
newer prompt builders that implement the LLM team's latest
instructions. The new prompt builders allow the service to leverage
few‑shot examples and deliver structured JSON outputs without
hand‑rolled schemas.
"""

from typing import List, Dict, Any

def build_system_prompt() -> str:
    return (
        "You are an expert academic evaluator. "
        "You classify submissions as AI, Human, or Hybrid; estimate confidence; "
        "score against rubric criteria (0-1); and write concise, constructive feedback. "
        "Always output STRICT JSON that matches the provided JSON schema."
    )

# ---------------------------------------------------------------------------
# New prompt helpers
#
# The LLM team provided a new prompt specification for two primary tasks:
# 1. Detection (classification) – determines whether a submission is
#    AI‑generated, human‑written, or hybrid. The model should output a
#    JSON object containing a label and a short list of reasoning points.
# 2. Feedback generation – produces an overall summary and per‑criterion
#    feedback including ratings and evidence aligned to rubric descriptors.
#
# These helpers construct the system and user messages to drive Gemini
# according to the latest specification. See the build_detection_prompt()
# and build_feedback_prompt() functions below.

def format_rubric(rubric: Dict[str, Any]) -> str:
    """
    Formats a rubric dictionary into a human‑readable multi‑line string.

    Each criterion is rendered with its ID, name, description and
    performance descriptors. The resulting string can be embedded into
    a prompt for feedback generation.

    Parameters
    ----------
    rubric : Dict[str, Any]
        A rubric dictionary containing an ID and a list of criteria. Each
        criterion may include performance descriptors.

    Returns
    -------
    str
        A formatted text block describing the rubric.
    """
    formatted_rubric = f"""
Rubric ID: {rubric.get('rubric_id', '')}
Criteria:
"""
    for rubric_item in rubric.get('criteria', []):
        formatted_rubric += f"""
  Criterion: {rubric_item.get('criterion_id', '')}
  Name: {rubric_item.get('name', '')}
  Description: {rubric_item.get('description', '')}
  Performance Descriptors:
"""
        pd = rubric_item.get('performance_descriptors') or {}
        for key, val in pd.items():
            formatted_rubric += f"\n    - {key}: {val}"
        formatted_rubric += "\n"
    return formatted_rubric


def create_few_shot_block(subs: List[Dict[str, Any]], max_examples: int = 3) -> str:
    """
    Select a few representative examples and format them for few‑shot prompting.

    The function attempts to include at least one example of each label
    (Human, AI, Hybrid) if available and then fills the remainder of
    slots up to `max_examples` with additional submissions.

    Parameters
    ----------
    subs : List[Dict[str, Any]]
        A list of submission dictionaries containing `final_submission`
        and `label_type` fields.
    max_examples : int, optional
        Maximum number of examples to include, by default 3.

    Returns
    -------
    str
        A formatted text block for few‑shot prompting, or a fallback
        message if no examples are available.
    """
    labels = ["Human", "AI", "Hybrid"]
    shots: List[Dict[str, Any]] = []

    # pick one example per label first
    for label in labels:
        for s in subs:
            if s.get("label_type", "").strip() == label:
                shots.append(s)
                break

    # fill remaining slots if needed
    for s in subs:
        if len(shots) >= max_examples:
            break
        if s not in shots:
            shots.append(s)

    # create the formatted few‑shot block
    if shots:
        return "\n\n".join(
            f'Submission: """{s.get("final_submission", "")}"""\nLabel: {s.get("label_type", "Unknown")}'
            for s in shots
        )

    return "/* no examples available */"


def build_detection_prompt(example_block: str, submission: str) -> Dict[str, str]:
    """
    Build a structured prompt for classifying submissions as Human, AI or Hybrid.

    The returned dictionary contains separate system and user messages.
    Gemini will be instructed to analyse the submission, compare against
    few‑shot examples and output a JSON object with a label and a list
    of reasons for the classification.

    Parameters
    ----------
    example_block : str
        A formatted few‑shot block produced by `create_few_shot_block()`.
    submission : str
        The submission text to classify.

    Returns
    -------
    Dict[str, str]
        A dictionary with `system` and `user` keys representing the
        messages to send to Gemini.
    """
    role = (
        "You are an impartial AI text detector evaluating whether a given text is AI-"
        " or human-generated or Hybrid."
    )
    task = (
        "Classify the text and provide reasoning for your decision."
    )
    step = (
        "Step 1: Analyze the text’s linguistic patterns and style.\n"
        "Step 2: Compare patterns to typical AI-generated and human-written texts.\n"
        "Step 3: Determine the label (AI-generated or human-written).\n"
        "Step 4: Provide reasoning"
    )
    system_prompt = f"""
{role}
Your task is to {task}
Following the {step}
Take the input:
    - 'Submission' which is submission.

{example_block}

Then output in this exact format (JSON):
    {{
        "label": "AI" or "Human" or "Hybrid",
        "reasoning": ["first reason", "second reason"]
    }}
"""

    user_prompt = (
        f"This the submission {submission}. Base on that provided me result"
    )
    return {
        "system": system_prompt,
        "user": user_prompt,
    }


def build_feedback_prompt(rubric_text: str, submission: str) -> Dict[str, str]:
    """
    Build a structured prompt for rubric‑aligned feedback generation.

    The model will be instructed to summarise the overall performance of
    the submission and then provide per‑criterion feedback, including
    ratings (e.g. excellent, good, average, needs_improvement, poor) and
    evidence drawn from the text. The caller must pass in a pre‑formatted
    rubric string produced by `format_rubric()`.

    Parameters
    ----------
    rubric_text : str
        A formatted rubric description returned by `format_rubric()`.
    submission : str
        The submission text to evaluate.

    Returns
    -------
    Dict[str, str]
        A dictionary containing `system` and `user` messages for Gemini.
    """
    role = (
        "You are a helpful and respectful educational assessment assistant that"
        " provides feedback on submitted work. Always answer as helpfully as"
        " possible, while being safe. Your answers should not include any"
        " harmful, unethical, racist, sexist, toxic, dangerous, or illegal"
        " content. Provide assessment feedback and a rating for the assessment"
        " based on performance descriptors."
    )
    task = "analyse the student’s response and generate detailed, actionable feedback"
    step = (
        "0. Summarize overall performance in 2-4 sentences of the input submission.\n"
        "1. Understand assignment context (domain, goals)\n"
        "2. Map submission to rubric descriptors\n"
        "3. Identify strengths (align with \"excellent\" or \"good\")\n"
        "4. Identify weaknesses (gaps, misalignments)\n"
        "5. Select concrete evidence from text\n"
        "6. Suggest actionable, domain-relevant improvements\n"
        "7. Ensure tone is constructive, professional, encouraging\n"
    )
    system_prompt = f"""
{role} and your task is to {task}.

Following the below step:\n{step}
{rubric_text}

Take the input as a text submission of the task and provide the output as these following:
 1) Overall Summary: 2–4 sentences on strengths and priorities.\n 2) Criteria Feedback: For each rubric criterion, include:\n     - Criterion\n     - Rating (excellent, good, average, needs_improvement, poor)\n     - Evidence (1–3 bullet points citing excerpts or behaviors)
"""
    user_prompt = (
        f"This is the submission of the student {submission} and provide the output"
    )
    return {
        "system": system_prompt,
        "user": user_prompt,
    }

def build_fewshot_block(fewshots: List[Dict]) -> str:
    lines = []
    for i, ex in enumerate(fewshots, 1):
        fs = ex.get("final_submission", "").strip().replace("\\n", " ")
        lt = ex.get("label_type", "Unknown")
        lines.append(f"### FEWSHOT {i}SUBMISSION: {fs} LABEL: {lt}")
    return "".join(lines)

def build_user_prompt(task: str, domain: str, prompt: str, rubric: Dict, submission: str) -> str:
    rubric_text = []
    for c in rubric.get("criteria", []):
        rubric_text.append(f"- {c.get('criterion_id')}: {c.get('name')} — {c.get('description','')}")
    rubric_block = "".join(rubric_text)

    return (
        f"DOMAIN: {domain}"
        f"TASK_PROMPT: {prompt}"
        f"RUBRIC:{rubric_block}"
        f"SUBMISSION:{submission}"
        f"RETURN: {task} as strict JSON. No markdown."
    )

def json_schema_for(task: str) -> Dict:
    if task == "classification":
        return {
            "type": "object",
            "properties": {
                "label": {"type": "string", "enum": ["AI", "Human", "Hybrid"]},
                "rationale": {"type": "string"}
            },
            "required": ["label", "rationale"]
        }
    if task == "confidence":
        return {
            "type": "object",
            "properties": {
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "basis": {"type": "string"}
            },
            "required": ["confidence", "basis"]
        }
    if task == "rubric-scores":
        return {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criterion_id": {"type": "string"},
                            "name": {"type": "string"},
                            "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "rationale": {"type": "string"}
                        },
                        "required": ["criterion_id", "name", "score", "rationale"]
                    }
                },
                "overall": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            },
            "required": ["scores", "overall"]
        }
    if task == "feedback":
        # New schema for structured feedback output. The model must
        # produce a single JSON object with six keys. Each key is
        # explicitly typed and constrained to ensure predictable
        # structure. No additional properties are permitted.
        return {
            "type": "object",
            "properties": {
                "overall_grade": {
                    "type": "string",
                    "enum": [
                        "excellent",
                        "good",
                        "average",
                        "needs improvement",
                        "poor",
                    ],
                },
                "reasoning": {"type": "string"},
                "criteria": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criterion_id": {"type": "string"},
                            "reasoning": {"type": "string"},
                            "rating": {
                                "type": "string",
                                "enum": [
                                    "excellent",
                                    "good",
                                    "average",
                                    "needs improvement",
                                    "poor",
                                ],
                            },
                        },
                        "required": ["criterion_id", "reasoning", "rating"],
                    },
                },
                "strengths": {"type": "string"},
                "weaknesses": {"type": "string"},
                "improvement_tips": {"type": "string"},
            },
            "required": [
                "overall_grade",
                "reasoning",
                "criteria",
                "strengths",
                "weaknesses",
                "improvement_tips",
            ],
            "additionalProperties": False,
        }
    if task == "evaluate":
        return {"type": "object"}
    return {"type": "object"}
