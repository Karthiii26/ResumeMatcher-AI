import importlib
import logging
import os
import time
from typing import Any


LOGGER = logging.getLogger("resumematch.startup")
MODEL_PATH = os.getenv("MODEL_PATH", "all-MiniLM-L6-v2")
WARMUP_TEXT = "ResumeMatch startup warmup sentence."

_MODEL: Any | None = None
_READY = False
_TIMINGS: dict[str, float] = {}


def _timed(label: str, fn):
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    _TIMINGS[label] = elapsed
    LOGGER.info("startup_timer.%s=%.3fs", label, elapsed)
    return result


def _configure_torch(torch_module) -> None:
    threads = int(os.getenv("TORCH_NUM_THREADS", "1"))
    torch_module.set_num_threads(threads)
    if hasattr(torch_module, "set_num_interop_threads"):
        try:
            torch_module.set_num_interop_threads(1)
        except RuntimeError:
            pass


def load_model() -> Any:
    global _MODEL, _READY
    if _MODEL is not None:
        return _MODEL

    torch = _timed("torch_import", lambda: importlib.import_module("torch"))
    _configure_torch(torch)
    _timed("transformers_import", lambda: importlib.import_module("transformers"))
    sentence_transformers = _timed(
        "sentence_transformers_import",
        lambda: importlib.import_module("sentence_transformers"),
    )

    SentenceTransformer = sentence_transformers.SentenceTransformer
    model_path = os.getenv("MODEL_PATH", MODEL_PATH)
    _MODEL = _timed(
        "minilm_load",
        lambda: SentenceTransformer(model_path, local_files_only=True),
    )
    _MODEL.eval()

    _timed(
        "first_inference",
        lambda: _MODEL.encode(
            [WARMUP_TEXT],
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ),
    )
    _READY = True
    return _MODEL


def get_model() -> Any:
    if _MODEL is None:
        return load_model()
    return _MODEL


def is_ready() -> bool:
    return _READY and _MODEL is not None


def startup_timings() -> dict[str, float]:
    return dict(_TIMINGS)
