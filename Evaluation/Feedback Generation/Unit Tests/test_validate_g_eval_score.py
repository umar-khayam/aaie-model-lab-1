import os
import pytest

from Evaluation.evaluate_model_genai import run_g_eval_evaluation


# ---------------- Configuration ---------------- #

DEFAULT_THRESHOLD = float(
    os.getenv("G_EVAL_THRESHOLD", 0.6)
)


# ---------------- Unit Test ---------------- #

def test_g_eval_score_above_threshold():
    """
    Ensures that the g-eval score meets the minimum
    quality threshold. Fails the test if quality regresses.
    """

    result = run_g_eval_evaluation()

    score = result.get("mean_score")

    assert score is not None, "No g-eval score returned"

    assert score >= DEFAULT_THRESHOLD, (
        f"g-eval score {score:.3f} is below threshold "
        f"{DEFAULT_THRESHOLD:.3f}"
    )
