"""
Cross-encoder reranker — 03 §10.
Supports BAAI/bge-reranker-v2-m3 with sigmoid scaling, score blending,
and fallback when reranker is disabled or weights are not loaded.
"""

import logging
import math
from typing import Any

from app.config import get_settings

logger = logging.getLogger("rgf.retrieval.reranker")


def sigmoid(x: float) -> float:
    """Standard sigmoid function mapping logits to (0, 1)."""
    return 1.0 / (1.0 + math.exp(-max(-50.0, min(50.0, x))))


class CrossEncoderReranker:
    """Cross-encoder reranker with graceful fallback."""

    def __init__(self):
        settings = get_settings()
        self.enabled = settings.reranker_enabled
        self.model_name = settings.reranker_model
        self.rerank_weight = settings.rerank_weight
        self.prior_weight = settings.prior_weight
        self._model: Any = None

    def _load_model(self):
        if self._model is None and self.enabled:
            try:
                from sentence_transformers import CrossEncoder
                logger.info("Loading CrossEncoder model %s...", self.model_name)
                self._model = CrossEncoder(self.model_name)
                logger.info("CrossEncoder model loaded successfully.")
            except Exception as e:
                logger.warning("Could not load CrossEncoder (%s); using prior scores.", e)
                self.enabled = False

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Rerank candidates using cross-encoder and blend with section prior."""
        if not candidates:
            return []

        if not self.enabled:
            # Fallback path: final_score = prior_score
            for c in candidates:
                c["rerank_score"] = c.get("prior_score", 0.0)
                c["final_score"] = c.get("prior_score", 0.0)
            candidates.sort(key=lambda x: x["final_score"], reverse=True)
            return candidates[:top_k]

        self._load_model()

        if self._model is None:
            for c in candidates:
                c["rerank_score"] = c.get("prior_score", 0.0)
                c["final_score"] = c.get("prior_score", 0.0)
            candidates.sort(key=lambda x: x["final_score"], reverse=True)
            return candidates[:top_k]

        # Prepare pairs: (query, "{section_heading}: {text}")
        pairs = [
            (query, f"{c.get('section_heading') or c.get('chunk_type', '')}: {c.get('text', '')}")
            for c in candidates
        ]

        try:
            scores = self._model.predict(pairs)
            for i, c in enumerate(candidates):
                raw_score = float(scores[i])
                r_score = sigmoid(raw_score)
                c["rerank_score"] = r_score

                # Blended final score: 0.85 * rerank + 0.15 * prior_normalized (03 §10)
                boost = c.get("section_boost", 0.0)
                norm_boost = min(1.0, boost / 0.20) if boost > 0 else 0.0
                c["final_score"] = (self.rerank_weight * r_score) + (self.prior_weight * norm_boost)

            candidates.sort(key=lambda x: x["final_score"], reverse=True)
            return candidates[:top_k]

        except Exception as exc:
            logger.exception("Cross-encoder inference failed: %s", exc)
            for c in candidates:
                c["final_score"] = c.get("prior_score", 0.0)
            candidates.sort(key=lambda x: x["final_score"], reverse=True)
            return candidates[:top_k]


# Singleton reranker instance
_reranker_instance: CrossEncoderReranker | None = None


def get_reranker() -> CrossEncoderReranker:
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = CrossEncoderReranker()
    return _reranker_instance
