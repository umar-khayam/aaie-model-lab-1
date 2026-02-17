"""Utilities for loading and interacting with GGUF-based LLMs via llama-cpp.

This module defines the :class:`ModelManager` class used throughout the
evaluation pipeline. It encapsulates model loading, unloading and simple
completion/chat interfaces. The implementation is designed to mirror the
behaviour of the original notebook while providing basic error handling
and reporting.

If `llama_cpp` or the GGUF model files are unavailable in the execution
environment, the methods will log a warning and return empty strings
instead of raising exceptions. This allows downstream steps to continue
executing and issue warnings rather than failing outright.
"""

from __future__ import annotations

import gc
import logging
from typing import Any, Dict, Optional, Sequence

try:
    import torch  # type: ignore
except Exception:
    torch = None  # type: ignore

try:
    # Importing llama_cpp can throw if the library isn't installed.
    from llama_cpp import Llama  # type: ignore
except Exception:
    Llama = None  # type: ignore

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading and caching of GGUF models for llama-cpp.

    The manager keeps track of the currently loaded model and its path. When
    requested to load a new model it will unload any existing model and
    attempt to initialise the new one. The caching behaviour mirrors the
    original notebook implementation: subsequent calls to load the same
    model will return the existing instance.
    """

    def __init__(self) -> None:
        self.current_model: Optional[Any] = None
        self.current_model_path: str = ""

    def load_model(self, repo_id: str, filename: str, n_ctx: int = 8192) -> Optional[Any]:
        """Load a GGUF model using llama-cpp.

        Parameters
        ----------
        repo_id: str
            The HuggingFace repository identifier.
        filename: str
            The model file name within the repository.
        n_ctx: int, optional
            The context window for the model (default 8192).

        Returns
        -------
        Llama | None
            The loaded model instance, or ``None`` if loading failed.
        """
        full_model_id = f"{repo_id}/{filename}"

        # return cached model if it's already loaded
        if self.current_model_path == full_model_id and self.current_model is not None:
            return self.current_model

        # Unload previously loaded model if any
        if self.current_model is not None:
            logger.info(f"Unloading model: {self.current_model_path}…")
            del self.current_model
            self.current_model = None
            gc.collect()
            # Get rid of GPU caches if available
            if torch is not None and getattr(torch, "cuda", None) is not None and torch.cuda.is_available():
                torch.cuda.empty_cache()

        logger.info(f"Loading model: {repo_id} ({filename})…")
        if Llama is None:
            logger.warning(
                "llama_cpp is not installed; cannot load model."
            )
            return None
        try:
            model = Llama.from_pretrained(
                repo_id=repo_id,
                filename=filename,
                n_gpu_layers=-1,
                n_ctx=n_ctx,
                verbose=False,
            )
            self.current_model = model
            self.current_model_path = full_model_id
            return model
        except Exception as exc:
            logger.error(f"Error loading model {full_model_id}: {exc}")
            self.current_model = None
            self.current_model_path = ""
            return None

    def _generate(
        self,
        method_name: str,
        *args: Any,
        repo_id: str,
        filename: str,
        max_tokens: int = 1024,
        temp: float = 0.3,
        stop: Optional[Sequence[str]] = None,
    ) -> str:
        """Internal helper to call either `create_completion` or `create_chat_completion`.

        Handles missing model or exceptions gracefully. This method centralises
        the generation logic used by both :meth:`generate_response` and
        :meth:`generate_chat_response`.
        """
        model = self.load_model(repo_id, filename)
        if model is None:
            logger.warning(
                f"Model {repo_id}/{filename} not loaded; returning empty string."
            )
            return ""
        try:
            if method_name == "create_completion":
                output = model.create_completion(
                    prompt=args[0],
                    max_tokens=max_tokens,
                    temperature=temp,
                    stop=stop if stop else [],
                )
                return output["choices"][0]["text"]
            elif method_name == "create_chat_completion":
                output = model.create_chat_completion(
                    messages=args[0],
                    max_tokens=max_tokens,
                    temperature=temp,
                    stop=stop if stop else [],
                )
                return output["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unknown generation method: {method_name}")
        except Exception as exc:
            logger.error(f"Error during {method_name}: {exc}")
            return ""

    def generate_response(
        self,
        prompt: str,
        repo_id: str,
        filename: str,
        max_tokens: int = 1024,
        temp: float = 0.3,
        stop: Optional[Sequence[str]] = None,
    ) -> str:
        """Generate a completion for a raw prompt using the specified model."""
        return self._generate(
            "create_completion",
            prompt,
            repo_id=repo_id,
            filename=filename,
            max_tokens=max_tokens,
            temp=temp,
            stop=stop,
        )

    def generate_chat_response(
        self,
        messages: Sequence[Dict[str, str]],
        repo_id: str,
        filename: str,
        max_tokens: int = 1024,
        temp: float = 0.3,
        stop: Optional[Sequence[str]] = None,
    ) -> str:
        """Generate a chat response using the specified model and message list."""
        return self._generate(
            "create_chat_completion",
            messages,
            repo_id=repo_id,
            filename=filename,
            max_tokens=max_tokens,
            temp=temp,
            stop=stop,
        )

__all__ = ["ModelManager"]