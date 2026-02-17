"""Resource cleanup utilities for the evaluation pipeline.

This module provides a helper to release the current model loaded by
``ModelManager`` and clear GPU caches if necessary. While Python's garbage
collector will eventually free resources, explicit cleanup can help in
long running processes to reduce memory pressure.
"""

from __future__ import annotations

import gc
import logging
from typing import Optional

try:
    import torch
except Exception:
    torch = None

from .model_manager import ModelManager

logger = logging.getLogger(__name__)


def cleanup(manager: Optional[ModelManager]) -> None:
    """Release any loaded models and clear caches.

    Parameters
    ----------
    manager: ModelManager | None
        The model manager instance to clear. If ``None``, only caches are
        emptied.
    """
    if manager is not None and hasattr(manager, "current_model"):
        try:
            if manager.current_model is not None:
                logger.info(f"Deleting current model {manager.current_model_path}…")
            del manager.current_model
            manager.current_model = None
            manager.current_model_path = ""
        except Exception as exc:
            logger.error(f"Error during cleanup: {exc}")
    # Trigger garbage collection
    gc.collect()
    if torch is not None and getattr(torch, "cuda", None) is not None and torch.cuda.is_available():
        torch.cuda.empty_cache()
    if torch is not None and getattr(torch.backends, "mps", None) is not None:
        gc.collect()
    logger.info("Resources cleared.")


__all__ = ["cleanup"]