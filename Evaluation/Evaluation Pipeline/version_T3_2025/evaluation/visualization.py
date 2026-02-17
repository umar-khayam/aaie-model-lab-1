"""Reporting utilities for summarising evaluation results.

This module assembles quantitative scoring metrics, averages DeepEval metrics and
optionally produces a confusion matrix and simple visualisations. When
graphical libraries are unavailable, it falls back to printing summary
tables and statistics.
"""

from __future__ import annotations

import logging
from typing import Dict, List

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from sklearn.metrics import cohen_kappa_score, mean_squared_error, confusion_matrix  # type: ignore
from scipy.stats import pearsonr, spearmanr  # type: ignore

logger = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt  # type: ignore
    import seaborn as sns  # type: ignore
    _HAS_PLOT = True
except Exception:
    _HAS_PLOT = False


def generate_visualizations(df: pd.DataFrame, config: Dict[str, Dict[str, str]]) -> None:
    """Produce a summary report and optional plots from the evaluation DataFrame.

    Parameters
    ----------
    df: pandas.DataFrame
        The evaluation DataFrame containing human scores, predicted scores and
        judge metrics.
    config: dict
        Configuration dictionary specifying output directories (currently unused).

    Notes
    -----
    This function prints formatted tables summarising the correlation metrics
    and average judge scores. If ``matplotlib`` and ``seaborn`` are available
    it additionally renders bar charts, scatter plots and a confusion matrix.
    """
    if df is None or df.empty:
        logger.warning("Empty or missing DataFrame passed to generate_visualizations.")
        return

    # Quantitative scoring metrics (pearson, spearman, mse, kappa)
    score_categories: List[str] = ["content", "organization", "language", "total"]
    quant_results: List[Dict[str, float]] = []

    for cat in score_categories:
        human_col = cat
        pred_col = f"pred_{cat}" if cat != "total" else "pred_total"
        
        # Ensure columns exist before processing for error handling
        if human_col not in df.columns or pred_col not in df.columns:
            continue

        valid_df = df.dropna(subset=[human_col, pred_col])
        if len(valid_df) > 1:
            try:
                p_corr, _ = pearsonr(valid_df[human_col], valid_df[pred_col])
                s_corr, _ = spearmanr(valid_df[human_col], valid_df[pred_col])
                mse = mean_squared_error(valid_df[human_col], valid_df[pred_col])
                
                human_int = valid_df[human_col].round().astype(int)
                pred_int = valid_df[pred_col].round().astype(int)
                
                qwk = cohen_kappa_score(human_int, pred_int, weights="quadratic")
                
                quant_results.append({
                    "Category": cat.capitalize(),
                    "QWK (Kappa)": qwk,
                    "Pearson (r)": p_corr,
                    "Spearman (rho)": s_corr,
                    "MSE": mse,
                })
            except Exception as exc:
                logger.error(f"Error computing quantitative metrics for {cat}: {exc}")

    if quant_results:
        quant_df = pd.DataFrame(quant_results).set_index("Category")
        print("\n--- A. SCORING PERFORMANCE METRICS ---")
        print(quant_df.round(3).to_string())
    else:
        print("No quantitative metrics computed.")

    # Judge metrics summary
    judge_cols = [c for c in df.columns if c.startswith("judge_") and not c.endswith("_reason")]
    if judge_cols:
        judge_summary = df[judge_cols].mean().round(3).to_frame(name="Average Score")
        judge_summary.index = [x.replace("judge_", "").capitalize() for x in judge_summary.index]
        print("\n--- B. LLM-AS-A-JUDGE METRICS (0.0 - 1.0) ---")
        print(judge_summary.to_string())
    else:
        print("No judge metrics available.")

    # Optional visualisations
    if _HAS_PLOT and quant_results and judge_cols:
        # Define Color Palette
        NICE_BLUE = "#66ACF3"   # Professional strong blue
        NICE_RED = "#F66F6F"    # Deep readable red
        BLACK = "#3B2F2F"       # Pure black for text

        # Force Global Styles for Black Text
        sns.set_theme(style="white")
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'text.color': BLACK,
            'axes.labelcolor': BLACK,
            'xtick.color': BLACK,
            'ytick.color': BLACK,
            'axes.titlecolor': BLACK,
            'axes.edgecolor': BLACK,
            'axes.grid': True,
            'grid.color': '#EEEEEE',
            'grid.linestyle': '--',
            'font.size': 11,
            'font.weight': 'normal'
        })

        # This provides 8 slots for your 7 plots.
        fig, axes = plt.subplots(4, 2, figsize=(20, 24)) 
        plt.subplots_adjust(hspace=0.4, wspace=0.3)

        # Plot 1: Quantitative metrics overview
        quant_subset = quant_df[["QWK (Kappa)", "Pearson (r)"]]
        quant_subset.plot(
            kind="bar", 
            ax=axes[0, 0], 
            color=[NICE_BLUE, NICE_RED], 
            edgecolor=BLACK,
            width=0.7
        )
        axes[0, 0].set_title("Scoring Reliability: QWK (Blue) vs Pearson (Red)", fontsize=14, pad=15)
        axes[0, 0].set_ylim(0, 1.0)
        axes[0, 0].legend(loc='lower right', frameon=True, facecolor='white', edgecolor='black')
        axes[0, 0].tick_params(axis='x', rotation=0)

        # Plot 2: Total score alignment scatter
        try:
            sns.regplot(
                data=df, 
                x='total', 
                y='pred_total', 
                ax=axes[0, 1],
                color=NICE_BLUE,
                scatter_kws={'s': 100, 'alpha': 0.6, 'edgecolor': NICE_BLUE},
                line_kws={'color': NICE_RED, 'linewidth': 2}
            )
            
            min_val = min(df['total'].min(), df['pred_total'].min())
            max_val = max(df['total'].max(), df['pred_total'].max())
            axes[0, 1].plot([min_val, max_val], [min_val, max_val], color=BLACK, linestyle='--', linewidth=1.5, label='Perfect Match')
            
            axes[0, 1].set_title("Total Score Alignment: Human vs Model", fontsize=14, pad=15)
            axes[0, 1].set_xlabel("Human Ground Truth")
            axes[0, 1].set_ylabel("Model Prediction")
            axes[0, 1].legend(frameon=True, facecolor='white', edgecolor='black')
        except Exception as exc:
            logger.error(f"Error creating scatter plot: {exc}")

        # Plot 3: Judge metrics bar chart
        avg_judge = df[judge_cols].mean()
        avg_judge.index = [x.replace('judge_', '').capitalize() for x in avg_judge.index]
        bar_colors = [NICE_RED if x < 0.6 else NICE_BLUE for x in avg_judge.values]
        
        sns.barplot(
            x=avg_judge.values, 
            y=avg_judge.index, 
            palette=bar_colors, 
            ax=axes[1, 0],
            edgecolor=BLACK
        )
        axes[1, 0].set_title("LLM-as-a-Judge Quality Scores (0.6 threshold)", fontsize=14, pad=15)
        axes[1, 0].set_xlim(0, 1.0)
        axes[1, 0].set_xlabel("Average Score (0-1)")
        
        for i, v in enumerate(avg_judge.values):
            axes[1, 0].text(v + 0.01, i, f"{v:.2f}", color=BLACK, va='center', fontweight='bold')

        # Plot 4: Confusion matrix for rounded total scores
        try:
            plot_df = df.dropna(subset=['total', 'pred_total'])
            h_total = plot_df['total'].round().astype(int)
            p_total = plot_df['pred_total'].round().astype(int)
            labels = sorted(list(set(h_total) | set(p_total)))
            
            cm = confusion_matrix(h_total, p_total, labels=labels)
            
            sns.heatmap(
                cm, 
                annot=True, 
                fmt='d', 
                cmap='Oranges',
                xticklabels=labels,
                yticklabels=labels, 
                ax=axes[1, 1],
                cbar_kws={'label': 'Count'},
                linecolor=BLACK,
                linewidths=0.5,
                annot_kws={"color": BLACK, "weight": "bold"}
            )
            axes[1, 1].set_title("Confusion Matrix: Total Score (Rounded)", fontsize=14, pad=15)
            axes[1, 1].set_xlabel("Model Predicted Total")
            axes[1, 1].set_ylabel("Human Total Score")
        except Exception as exc:
            logger.error(f"Error creating confusion matrix: {exc}")

        # Plot 5: Confusion matrix content scores
        try:
            plot_df = df.dropna(subset=['content', 'pred_content'])
            h_content = plot_df['content'].round().astype(int)
            p_content = plot_df['pred_content'].round().astype(int)
            labels = sorted(list(set(h_content) | set(p_content)))
            
            cm = confusion_matrix(h_content, p_content, labels=labels)
            
            sns.heatmap(
                cm, 
                annot=True,
                fmt='d', 
                cmap='Oranges',
                xticklabels=labels,
                yticklabels=labels, 
                ax=axes[2, 0], 
                cbar_kws={'label': 'Count'},
                linecolor=BLACK,
                linewidths=0.5,
                annot_kws={"color": BLACK, "weight": "bold"}
            )
            axes[2, 0].set_title("Confusion Matrix: Content Score (Rounded)", fontsize=14, pad=15)
            axes[2, 0].set_xlabel("Model Predicted Content")
            axes[2, 0].set_ylabel("Human Content Score")
        except Exception as exc:
            logger.error(f"Error creating content confusion matrix: {exc}")

        # Plot 6: Confusion matrix organization scores
        try:
            plot_df = df.dropna(subset=['organization', 'pred_organization'])
            h_org = plot_df['organization'].round().astype(int)
            p_org = plot_df['pred_organization'].round().astype(int)
            labels = sorted(list(set(h_org) | set(p_org)))
            
            cm = confusion_matrix(h_org, p_org, labels=labels)
            
            sns.heatmap(
                cm, 
                annot=True,
                fmt='d', 
                cmap='Oranges',
                xticklabels=labels,
                yticklabels=labels, 
                ax=axes[2, 1],
                cbar_kws={'label': 'Count'},
                linecolor=BLACK,
                linewidths=0.5,
                annot_kws={"color": BLACK, "weight": "bold"}
            )
            axes[2, 1].set_title("Confusion Matrix: Organization Score (Rounded)", fontsize=14, pad=15)
            axes[2, 1].set_xlabel("Model Predicted Organization")
            axes[2, 1].set_ylabel("Human Organization Score")
        except Exception as exc:
            logger.error(f"Error creating organization confusion matrix: {exc}")

        # Plot 7: Confusion matrix language scores
        try:
            plot_df = df.dropna(subset=['language', 'pred_language'])
            h_lang = plot_df['language'].round().astype(int)
            p_lang = plot_df['pred_language'].round().astype(int)
            labels = sorted(list(set(h_lang) | set(p_lang)))
            
            cm = confusion_matrix(h_lang, p_lang, labels=labels)

            sns.heatmap(
                cm, 
                annot=True,
                fmt='d', 
                cmap='Oranges',
                xticklabels=labels,
                yticklabels=labels, 
                ax=axes[3, 0],
                cbar_kws={'label': 'Count'},
                linecolor=BLACK,
                linewidths=0.5,
                annot_kws={"color": BLACK, "weight": "bold"}
            )
            axes[3, 0].set_title("Confusion Matrix: Language Score (Rounded)", fontsize=14, pad=15)
            axes[3, 0].set_xlabel("Model Predicted Language")
            axes[3, 0].set_ylabel("Human Language Score")
        except Exception as exc:
            logger.error(f"Error creating language confusion matrix: {exc}")
        
        # Turn off the empty slot at bottom right (3, 1) otherwise chaoss ensues
        axes[3, 1].axis('off')

        plt.tight_layout()
        plt.show()

    # Qualitative sample
    if not df.empty:
        try:
            sample = df.sample(1).iloc[0]
            print("\n==========================================")
            print("       QUALITATIVE ANALYSIS SAMPLE")
            print("==========================================")
            if 'id' in sample:
                print(f"Essay ID: {sample['id']}")
            if 'total' in sample and 'pred_total' in sample:
                print(f"Human Total: {sample['total']} | Model Total: {sample['pred_total']}")
            print("-" * 60)
            if 'pred_feedback' in sample:
                print(f"[MODEL FEEDBACK]:\n{sample['pred_feedback']}")
            print("-" * 60)
            reason_cols = [c for c in df.columns if c.endswith('_reason')]
            if reason_cols:
                for r_col in reason_cols:
                    if pd.notna(sample[r_col]):
                        print(f"[{r_col.upper()}]: {sample[r_col]}")
                        break
            print("-" * 60)
        except Exception as e:
            logger.error(f"Error printing qualitative sample: {e}")


__all__ = ["generate_visualizations"]