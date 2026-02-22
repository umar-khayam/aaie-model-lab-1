"""Generation of reference ("gold") feedback using the ground-truth model.

This module defines a helper function for producing constructive feedback
for each row in the dataset. It relies on the :class:`ModelManager`
instance passed in from the caller to generate chat completions. The
function ``generate_gold_feedback_for_df`` applies this logic across an
entire DataFrame, adds a ``gold_feedback`` column and persists the
intermediate results to disk.

If the LLM is unavailable or any error occurs during generation, the
feedback for that row will be an empty string and a warning will be
logged. This ensures that downstream processing can proceed without
failing entirely.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict

import pandas as pd  # type: ignore
from tqdm import tqdm  # type: ignore

from .model_manager import ModelManager

logger = logging.getLogger(__name__)


def generate_gold_feedback(row: pd.Series, manager: ModelManager, config: Dict[str, Dict[str, str]]) -> str:
    """Generate a gold feedback string for a single row using the ground-truth model.

    The prompt is created and
    instructs the model to provide concise, constructive feedback wrapped
    within ``[FEEDBACK]`` tags. After generation, the helper attempts to
    extract the content between these tags and perform basic cleaning to
    remove any unwanted artefacts.

    Parameters
    ----------
    row: pandas.Series
        A row from the dataset containing at least ``prompt``, ``essay``
        and the score columns ``content``, ``organization``, ``language``
        and ``total``.
    manager: ModelManager
        The model manager used to invoke the LLM.
    config: dict
        The configuration dictionary containing the ground truth model
        specification.

    Returns
    -------
    str
        The cleaned feedback string. If generation fails, an empty string.
    """
    try:
        messages = [
            {"role": "system", "content": "You are an expert academic evaluator."},
            {
                "role": "user",
                "content": (
                    f"Task: Provide constructive feedback for the following student essay based on the assigned scores.\n\n"
                    f"Prompt: {row.get('prompt', '')}\n"
                    f"Student Essay: {row.get('essay', '')}\n\n"
                    f"Assigned Scores:\n"
                    f"- Content: {row.get('content', '')}\n"
                    f"- Organization: {row.get('organization', '')}\n"
                    f"- Language: {row.get('language', '')}\n"
                    f"- Total: {row.get('total', '')}\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Provide a concise paragraph (3-4 sentences) justifying the scores.\n"
                    "2. Do NOT output any \"thinking\" or conversational filler.\n"
                    "3. You MUST wrap your final feedback inside [FEEDBACK] tags.\n\n"
                    "Format:\n"
                    "[FEEDBACK]\n"
                    "(Your feedback text here)\n"
                    "[/FEEDBACK]"
                ),
            },
        ]
        # Generate chat response using the ground truth model
        repo = config["ground_truth_model"]["repo"]
        filename = config["ground_truth_model"]["file"]
        response = manager.generate_chat_response(
            messages,
            repo,
            filename,
            max_tokens=600,
            temp=0.3,
            stop=["[/FEEDBACK]"]
        )
    except Exception as exc:
        logger.error(f"Error generating gold feedback for row {getattr(row, 'name', 'unknown')}: {exc}")
        return ""

    if not isinstance(response, str):
        return ""
    clean_feedback = response.strip()
    # Attempt to extract the content inside [FEEDBACK] tags
    match = re.search(r"\[FEEDBACK\](.*?)(\[/FEEDBACK\]|$)", response, re.DOTALL | re.IGNORECASE)
    if match:
        clean_feedback = match.group(1).strip()
    # Remove known junk phrases
    junk_phrases = [
        "We need to", "Let's produce", "INSTRUCTIONS:", "Provide a concise",
        "The paragraph should", "We must not", "The essay scores reflect",
    ]
    for phrase in junk_phrases:
        if phrase in clean_feedback:
            clean_feedback = clean_feedback.split(phrase)[0].strip()
    # Final cleanup of [FEEDBACK] tags
    clean_feedback = re.sub(r"\[/?FEEDBACK\]", "", clean_feedback, flags=re.IGNORECASE).strip()
    return clean_feedback


def generate_gold_feedback_for_df(
    df: pd.DataFrame, manager: ModelManager, config: Dict[str, Dict[str, str]]
) -> pd.DataFrame:
    """Apply gold feedback generation across a DataFrame.

    The resulting DataFrame will have a new ``gold_feedback`` column. The
    updated DataFrame is saved to CSV and Parquet files in the configured
    output directory under the names ``df_gold_feedback_generated.csv``
    and ``df_gold_feedback_generated.parquet``.

    Parameters
    ----------
    df: pandas.DataFrame
        The input dataset.
    manager: ModelManager
        The model manager used for LLM invocations.
    config: dict
        The configuration dictionary specifying the ground truth model and
        output directory.

    Returns
    -------
    pandas.DataFrame
        The DataFrame with an added ``gold_feedback`` column.
    """
    if df is None or df.empty:
        logger.warning("Empty or missing DataFrame passed to gold feedback generation.")
        return df
    logger.info("Starting Stage 1: Generating Clean Gold Feedback…")
    tqdm.pandas(desc="\n\nGenerating Gold Feedback")
    df = df.copy()
    df["gold_feedback"] = df.progress_apply(lambda row: generate_gold_feedback(row, manager, config), axis=1)
    # Persist to disk
    output_dir = config.get("output_dir", "")
    try:
        if output_dir:
            csv_path = os.path.join(output_dir, "df_gold_feedback_generated.csv")
            parquet_path = os.path.join(output_dir, "df_gold_feedback_generated.parquet")
            df.to_csv(csv_path, index=False)
            df.to_parquet(parquet_path, index=False)
    except Exception as exc:
        logger.error(f"Failed to write gold feedback files: {exc}")
    # Show a sample for sanity if available
    if not df.empty and "gold_feedback" in df.columns:
        logger.info(f"\n\nSample gold feedback: {df['gold_feedback'].iloc[0][:100]}…\n")
    return df


__all__ = ["generate_gold_feedback", "generate_gold_feedback_for_df"]