"""Inference using the subject model and parsing of its outputs.

This module defines helper functions to query the subject model with a grading
prompt, parse the returned scores and feedback, and apply this to an
entire DataFrame. Results are persisted in the configured output
directory.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, Optional

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from tqdm import tqdm  # type: ignore

from .model_manager import ModelManager

logger = logging.getLogger(__name__)


# The system prompt used to instruct the subject model. This is stored as a
# module‑level constant to avoid recreating the long string on each call.
SYSTEM_PROMPT = """You are an expert academic IELTS/TOEFL evaluator. Your task is to grade student essays with high precision.

### SCORING RUBRIC
1. CONTENT (1-5): 
   - 5 (Strong): Fully addresses task; well-developed, supported ideas.
   - 3 (Moderate): Addresses task; development is repetitive or vague.
   - 1 (Weak): Irrelevant or incoherent.
2. ORGANIZATION (1-5):
   - 5 (Strong): Logical progression; effective transitions.
   - 3 (Moderate): Coherent but mechanical; inadequate paragraphing.
   - 1 (Weak): No logical structure.
3. LANGUAGE (1-5):
   - 5 (Strong): Natural, complex structures; minimal errors.
   - 3 (Moderate): Mix of simple/complex; noticeable errors but meaning is clear.
   - 1 (Weak): Excessive errors impede communication.

### RESPONSE FORMAT
You must strictly follow this format (plain text, no markdown, no intro):
Content Score: <int>
Content Feedback: <2-3 sentences. Identify weakness -> Quote text -> Explain fix.>
Organization Score: <int>
Organization Feedback: <2-3 sentences. Identify weakness -> Quote text -> Explain fix.>
Language Score: <int>
Language Feedback: <2-3 sentences. Identify weakness -> Quote text -> Explain fix.>

### EXAMPLES

User:
Essay Prompt: Do you agree that technology makes life easier?
Student Essay: Technology is good. It help people do things fast. For example car help travel. But sometimes bad. I think technology make life easy because computer and phone.

Assistant:
Content Score: 2
Content Feedback: The essay addresses the topic but lacks depth and development. The argument "Technology is good" is too simplistic. To improve, expand on the "sometimes bad" point with specific examples like social isolation.
Organization Score: 2
Organization Feedback: Ideas are disjointed and lack logical progression. The jump from "car help travel" to "sometimes bad" is abrupt. Use a transition like "On the other hand" to introduce counterarguments.
Language Score: 2
Language Feedback: The writing relies on very simple sentences with frequent grammar errors. "It help people" should be "It helps people." Try combining sentences using conjunctions like "because" or "although" to add complexity.

User:
Essay Prompt: Should students wear uniforms?
Student Essay: I strongly believe students should wear uniforms. Firstly, it saves time in the morning. As the saying goes, "time is money." Secondly, it prevents bullying based on clothing brands. Students wont tease each other about expensive clothes. Finally, it creates a sense of belonging. Everyone looks the same, so they feel like a team. Therefore, uniforms are beneficial.

Assistant:
Content Score: 5
Content Feedback: The essay fully addresses the task with relevant and well-supported ideas. The points about saving time and preventing bullying are persuasive. No major changes are needed for content, perhaps add a specific example of school unity.
Organization Score: 5
Organization Feedback: The structure is logical and cohesive. Transitions like "Firstly," "Secondly," and "Finally" guide the reader smoothly. The conclusion effectively summarizes the main arguments.
Language Score: 4
Language Feedback: The language is natural and generally accurate. However, "Students wont tease" is missing an apostrophe in "won't." Ensure strictly correct punctuation to achieve a perfect score.

User:
Essay Prompt: Is it better to live in the city or countryside?
Student Essay: City is loud. Cars everywhere. I like trees. Countryside is quiet. People are nice there. In city, people busy. I want live in farm. The air is clean.

Assistant:
Content Score: 3
Content Feedback: The position is clear, but the ideas are repetitive and underdeveloped. The comparison focuses mainly on noise and air. Elaborate on *why* "people are nice there" with a specific anecdote or observation.
Organization Score: 2
Organization Feedback: The essay lacks clear paragraphing and flow. It reads as a list of simple observations like "City is loud." Group related ideas (e.g., environment vs. social aspects) into distinct paragraphs.
Language Score: 2
Language Feedback: The text uses fragmented, simple sentences. "I want live in farm" should be "I want to live on a farm." Practice using full sentences with subjects and verbs to improve readability.

User:
Essay Prompt: Discuss the impact of social media.
Student Essay: Social media has revolutionized how we communicate. However, it has downsides. Cyberbullying is a major issue. "Many teenagers suffer from depression due to online harassment." This is a serious problem. Also, fake news spreads fast. People believe what they see. We need to be careful.

Assistant:
Content Score: 4
Content Feedback: The main parts of the task are addressed with relevant ideas like cyberbullying and fake news. The quote supports the argument well. To get a 5, deepen the analysis of *how* fake news impacts society specifically.
Organization Score: 3
Organization Feedback: The ideas are coherent but the transitions are mechanical. "Also, fake news spreads fast" is a bit abrupt. Use a stronger transition like "Furthermore, another significant challenge is..." to connect the points.
Language Score: 4
Language Feedback: Vocabulary is adequate (e.g., "revolutionized," "harassment"), but sentence structures are somewhat repetitive. "People believe what they see" is simple; try "Individuals often accept online information at face value without verification."

User:
Essay Prompt: The importance of sports in school.
Student Essay: Sports are fun.

Assistant:
Content Score: 1
Content Feedback: The content is virtually non-existent and fails to address the prompt in any meaningful way. "Sports are fun" is an opinion, not an essay. You must provide reasons and details to support your view.
Organization Score: 1
Organization Feedback: There is no structure to evaluate as there is only one sentence. An essay requires an introduction, body paragraphs, and a conclusion.
Language Score: 5
Language Feedback: The single sentence provided is grammatically correct. However, the extreme brevity prevents a demonstration of complex language skills needed for a high score.
"""


def query_subject_model(row: pd.Series, manager: ModelManager, config: Dict[str, Dict[str, str]]) -> str:
    """Query the subject model to obtain scores and feedback for a single row.

    Parameters
    ----------
    row: pandas.Series
        Row from the DataFrame containing at least the ``prompt`` and ``essay`` fields.
    manager: ModelManager
        The model manager used to invoke the subject model.
    config: dict
        Configuration dictionary containing the subject model's repo and file.

    Returns
    -------
    str
        The raw output from the subject model. If generation fails, an empty string.
    """
    user_prompt = f"Essay Prompt: {row.get('prompt', '')}\nStudent Essay: {row.get('essay', '')}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    repo = config["subject_model"]["repo"]
    filename = config["subject_model"]["file"]
    try:
        return manager.generate_chat_response(messages, repo, filename)
    except Exception as exc:
        logger.error(f"Error querying subject model for row {getattr(row, 'name', 'unknown')}: {exc}")
        return ""


def parse_model_output(text: Optional[str]) -> pd.Series:
    """Parse the raw text output from the subject model into scores and feedback.

    The function searches for patterns like ``Content Score: X`` to extract the
    numeric values for each criterion. It also extracts the feedback text by
    isolating sections following ``Content Feedback:``, ``Organization Feedback:``
    and ``Language Feedback:``. If parsing fails, NaNs and the raw text are
    returned as a fallback.

    Parameters
    ----------
    text: str | None
        Raw output string returned by the subject model. Can be ``None``.

    Returns
    -------
    pandas.Series
        A series containing ``pred_content``, ``pred_organization``,
        ``pred_language`` and ``pred_feedback``.
    """
    if text is None or not isinstance(text, str):
        return pd.Series([np.nan, np.nan, np.nan, text], index=["pred_content", "pred_organization", "pred_language", "pred_feedback"])
    scores = {"Content": np.nan, "Organization": np.nan, "Language": np.nan}
    # Parse numeric scores
    for crit in scores.keys():
        match = re.search(fr"{crit} Score:\s*([0-9.]+)", text, re.IGNORECASE)
        if match:
            try:
                scores[crit] = float(match.group(1))
            except Exception:
                scores[crit] = np.nan
    # Extract feedback sections
    feedback_parts = []
    # Remove the score declarations to simplify extraction
    cleaner_text = re.sub(r"(Content|Organization|Language) Score: \d+(\.\d+)?", "", text)
    for crit in ["Content", "Organization", "Language"]:
        pattern = fr"{crit} Feedback:\s*(.*?)(?=(Content|Organization|Language) Feedback:|$)"
        match = re.search(pattern, cleaner_text, re.IGNORECASE | re.DOTALL)
        if match:
            section = match.group(1).strip()
            feedback_parts.append(f"[{crit}]: {section}")
    full_feedback = "\n\n".join(feedback_parts) if feedback_parts else text.strip()
    return pd.Series([scores["Content"], scores["Organization"], scores["Language"], full_feedback], index=["pred_content", "pred_organization", "pred_language", "pred_feedback"])


def run_subject_model_inference(
    df: pd.DataFrame, manager: ModelManager, config: Dict[str, Dict[str, str]]
) -> pd.DataFrame:
    """Run the subject model inference pipeline on an entire DataFrame.

    The function adds the columns ``model_raw_output``, ``pred_content``,
    ``pred_organization``, ``pred_language``, ``pred_feedback`` and
    ``pred_total``. Intermediate results are saved to CSV and Parquet in
    ``config['output_dir']``.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data with prompts and essays.
    manager: ModelManager
        Model manager used to call the subject model.
    config: dict
        Configuration dictionary containing model specifications and
        output directory.

    Returns
    -------
    pandas.DataFrame
        DataFrame augmented with prediction columns.
    """
    if df is None or df.empty:
        logger.warning("Empty or missing DataFrame passed to subject model inference.")
        return df
    logger.info("Starting Stage 2: Inference with the subject model…")
    df = df.copy()
    tqdm.pandas(desc="Subject Model Inference")
    # Raw model output
    df["model_raw_output"] = df.progress_apply(
        lambda row: query_subject_model(row, manager, config), axis=1
    )
    # Parse the output into scores and feedback
    parsed = df["model_raw_output"].apply(parse_model_output)
    df[["pred_content", "pred_organization", "pred_language", "pred_feedback"]] = parsed
    df["pred_total"] = (
        df["pred_content"].fillna(0)
        + df["pred_organization"].fillna(0)
        + df["pred_language"].fillna(0)
    )
    # Persist results
    output_dir = config.get("output_dir", "")
    try:
        if output_dir:
            csv_path = os.path.join(output_dir, "df_predictions_evaluation_v2_results.csv")
            parquet_path = os.path.join(output_dir, "df_predictions_evaluation_v2_results.parquet") # Not really needed but nice to have
            df.to_csv(csv_path, index=False)
            df.to_parquet(parquet_path, index=False)
    except Exception as exc:
        logger.error(f"Failed to write subject model inference results: {exc}")
    # Display a sample of raw output
    if not df.empty and "model_raw_output" in df.columns:
        logger.info(f"Inference complete. Sample output:\n{df['model_raw_output'].iloc[0]}")
    return df


__all__ = [
    "query_subject_model",
    "parse_model_output",
    "run_subject_model_inference",
]