"""Computation of quantitative evaluation metrics.

This module calculates correlations, mean squared error, quadratic weighted kappa and
optionally BERTScore between the human scores and model predictions. The
results are returned as a dictionary and stored on the DataFrame.

If the ``bert_score`` library is not available in the environment the
corresponding metric will be skipped and NaN values will be used instead.
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from sklearn.metrics import cohen_kappa_score, mean_squared_error  # type: ignore
from scipy.stats import pearsonr, spearmanr  # type: ignore

logger = logging.getLogger(__name__)

try:
    from bert_score import score as bert_score_fn  # type: ignore
except Exception:
    bert_score_fn = None  # type: ignore


def calculate_metrics(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Compute evaluation metrics and attach results to the DataFrame.

    Parameters
    ----------
    df: pandas.DataFrame
        The DataFrame containing human scores (``content``, ``organization``,
        ``language``, ``total``), predicted scores (``pred_content``,
        ``pred_organization``, ``pred_language``, ``pred_total``) and
        feedback columns.

    Returns
    -------
    df: pandas.DataFrame
        The input DataFrame with an additional ``bert_score_f1`` column
        attached if BERTScore can be computed; otherwise, the column
        contains NaNs.
    metrics: dict
        A dictionary mapping metric names to their aggregated values (e.g.,
        pearson correlations, kappa scores and average BERTScore).
    """
    if df is None or df.empty:
        logger.warning("Empty or missing DataFrame passed to calculate_metrics.")
        print("Trying to load previous saved results from disk…")
        try:
            # Make sure this filename matches exactly what you have on disk
            df = pd.read_csv("/Users/matto/Documents/_Testing_evaluation/llm_evaluation/output/df_predictions_evaluation_v2_results.csv")
        except FileNotFoundError:
            logger.error("Could not find the results CSV file.")
            return pd.DataFrame(), {}
            
        if df.empty:
            logger.error("Loaded DataFrame is empty.")
            return df, {}
            
        logger.info(f"Successfully loaded {len(df)} rows from disk.")
    metrics: Dict[str, float] = {}
    # Compute correlations, MSE and kappa
    for criterion in ["content", "organization", "language", "total"]:
        human_col = criterion
        pred_col = f"pred_{criterion}" if criterion != "total" else "pred_total"
        valid_df = df.dropna(subset=[human_col, pred_col])
        if len(valid_df) > 1:
            try:
                pearson_val = pearsonr(valid_df[human_col], valid_df[pred_col])[0]
                spearman_val = spearmanr(valid_df[human_col], valid_df[pred_col])[0]
                mse_val = mean_squared_error(valid_df[human_col], valid_df[pred_col])
                human_int = valid_df[human_col].round().astype(int)
                pred_int = valid_df[pred_col].round().astype(int)
                kappa_val = cohen_kappa_score(human_int, pred_int, weights="quadratic")
                metrics[f"{criterion}_pearson"] = pearson_val
                metrics[f"{criterion}_spearman"] = spearman_val
                metrics[f"{criterion}_mse"] = mse_val
                metrics[f"{criterion}_kappa"] = kappa_val
            except Exception as exc:
                logger.error(f"Error computing metrics for {criterion}: {exc}")
    # Compute BERTScore if available
    if bert_score_fn is None:
        logger.warning("bert_score library not available; skipping BERTScore computation.")
        df["bert_score_f1"] = np.nan
        metrics["avg_bert_score"] = np.nan
    else:
        try:
            logger.info("Calculating BERTScore…")
            P, R, F1 = bert_score_fn(
                list(df["pred_feedback"].fillna("No feedback")),
                list(df["gold_feedback"].fillna("No feedback")),
                lang="en",
                verbose=False,
            )
            # Convert to numpy and attach to DataFrame
            df["bert_score_f1"] = F1.numpy()
            metrics["avg_bert_score"] = float(df["bert_score_f1"].mean())
        except Exception as exc:
            logger.error(f"Error computing BERTScore: {exc}")
            df["bert_score_f1"] = np.nan
            metrics["avg_bert_score"] = np.nan
    logger.info(f"Metrics computed: {metrics}")
    return df, metrics
    
    # Can build these metrics out further if needed

__all__ = ["calculate_metrics"]