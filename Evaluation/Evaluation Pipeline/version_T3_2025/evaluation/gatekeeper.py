"""Citation recall metric to assess referential integrity in feedback.

The citation recall metric examines whether contiguous
n-grams from the predicted feedback appear in the original essay. This
provides a rough measure of how well the feedback cites the student's
submission when making claims or suggestions.

The default n-gram size is 3, corresponding to trigrams. If either the
essay or the feedback is missing for a row, a recall of 0.0 is returned.
"""

from __future__ import annotations

import logging
import string
from typing import Optional

import pandas as pd  # type: ignore

logger = logging.getLogger(__name__)


def calculate_citation_recall(row: pd.Series, ngram_size: int = 3) -> float:
    """Compute the citation recall for a single row.

    The metric computes the fraction of contiguous n-grams in the feedback
    text that also appear somewhere in the essay text after normalization.

    Parameters
    ----------
    row: pandas.Series
        Row containing at least ``essay`` and ``pred_feedback`` columns.
    ngram_size: int, optional
        Size of the n-grams to compare (default is 3).

    Returns
    -------
    float
        The citation recall value between 0.0 and 1.0.
    """
    essay = row.get("essay")
    feedback = row.get("pred_feedback")
    if not isinstance(essay, str) or not isinstance(feedback, str):
        return 0.0
    def normalize(text: str) -> str:
        return text.lower().translate(str.maketrans('', '', string.punctuation))
    essay_text = normalize(essay)
    feedback_text = normalize(feedback)
    feedback_words = feedback_text.split()
    if len(feedback_words) < ngram_size:
        return 0.0
    # build n‑gram list
    feedback_ngrams = [
        " ".join(feedback_words[i : i + ngram_size])
        for i in range(len(feedback_words) - ngram_size + 1)
    ]
    matches = sum(1 for gram in feedback_ngrams if gram in essay_text)
    return matches / len(feedback_ngrams) if feedback_ngrams else 0.0


def apply_citation_recall(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate citation recall for each row and attach to the DataFrame.

    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame containing at least ``essay`` and ``pred_feedback`` columns.

    Returns
    -------
    pandas.DataFrame
        DataFrame with a new column ``citation_recall`` containing the
        calculated scores. If the DataFrame is empty, it is returned
        unchanged.
    """
    if df is None or df.empty:
        logger.warning("Empty or missing DataFrame passed to apply_citation_recall.")
        return df
    df = df.copy()
    df["citation_recall"] = df.apply(lambda x: calculate_citation_recall(x), axis=1)
    logger.info(f"Average citation recall: {df['citation_recall'].mean():.4f}")
    return df


__all__ = ["calculate_citation_recall", "apply_citation_recall"]