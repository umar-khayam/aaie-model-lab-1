"""Configuration and data loading utilities.

This module exposes a single global ``CONFIG`` dictionary containing all
settings used throughout the evaluation pipeline. It also provides helper
functions to load datasets and ensure output directories exist.

If the configured ``data_path`` does not exist on disk the loader will
return ``None`` and issue a warning rather than raising an exception.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import pandas as pd  # type: ignore

logger = logging.getLogger(__name__)


# --- Default configuration ---
# Adjust ``data_path`` and ``output_dir`` as needed to suit your environment.
CONFIG: Dict[str, Any] = {
    # Location of the TSV data file. Update this to point at your dataset.
    "data_path": "<PATH>/DREsS_dataset/DREsS_New.tsv",
    # Directory where intermediate results will be written. Defaults to a
    # relative ``output`` folder if the original path is not writable. Feel free
    # to override this in your own config via :func:`get_config`.
    "output_dir": "output",
    # Model definitions (GGUF)
    "ground_truth_model": {
        "repo": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        "file": "Meta-Llama-3.1-8B-Instruct-IQ2_M.gguf",
    },
    "subject_model": {
        "repo": "unsloth/Llama-3.2-3B-Instruct-GGUF",
        "file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
    },
    # Judge model for DeepEval
    "judge_model": {
        "repo": "unsloth/Qwen2.5-VL-7B-Instruct-GGUF",
        "file": "Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf",
    },
    # Meta Analysis model for final review and Explanation of results
    "meta_analysis_model": {
        "repo": "unsloth/gpt-oss-20b-GGUF",
        "file": "gpt-oss-20b-Q4_K_M.gguf" 
    },
    # Test settings
    "sample_size": 400,
    "max_tokens": 1024,
    "temp": 0.0,
}


def get_config() -> Dict[str, Any]:
    """Return a copy of the global configuration dictionary."""
    return dict(CONFIG)


def load_data(config: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """Load the TSV dataset specified in ``config['data_path']``.

    The file is read as a tab‑separated values file using :func:`pandas.read_csv`.
    The resulting frame is subsampled to ``config['sample_size']`` rows if
    specified and column names are stripped of whitespace. The output directory
    defined by ``config['output_dir']`` is created if it does not already exist.

    Parameters
    ----------
    config: dict
        Configuration dictionary containing at least ``data_path``, ``output_dir``
        and optionally ``sample_size``.

    Returns
    -------
    pandas.DataFrame | None
        The loaded DataFrame, or ``None`` if loading fails.
    """
    data_path = config.get("data_path")
    if not data_path:
        logger.warning("No data path provided in config; returning None.")
        return None
    # Ensure output directory exists
    output_dir = config.get("output_dir")
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as exc:
            logger.error(f"Could not create output directory {output_dir}: {exc}")
    # Attempt to load the file
    try:
        df = pd.read_csv(data_path, sep="\t")
    except FileNotFoundError:
        logger.warning(f"Data file not found: {data_path}. Returning None.")
        return None
    except Exception as exc:
        logger.error(f"Error loading data file {data_path}: {exc}")
        return None
    # Subsample if requested
    sample_size = config.get("sample_size")
    if isinstance(sample_size, int) and sample_size > 0 and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    # Clean column names
    df.columns = df.columns.str.strip()
    logger.info(f"Loaded dataset with {len(df)} rows.")
    return df


__all__ = ["CONFIG", "get_config", "load_data"]