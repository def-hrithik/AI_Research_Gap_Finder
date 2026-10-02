"""
Embedder protocol and implementations — 03 §5.
Supports sentence-transformers / BAAI/bge-m3 and a deterministic StubEmbedder.
"""

from abc import ABC, abstractmethod
import hashlib
import logging
from typing import Any
import numpy as np

from app.config import get_settings

logger = logging.getLogger("rgf.embeddings")


class BaseEmbedder(ABC):
    """Abstract embedder protocol."""

    @property
    @abstractmethod
    def dim(self) -> int:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """Embed a batch of document chunks.

        Returns:
            np.ndarray of shape (len(texts), dim) with float32 L2-normalized rows.
        """
        pass

    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single search query.

        Returns:
            np.ndarray of shape (dim,) with float32 L2-normalized vector.
        """
        pass


class StubEmbedder(BaseEmbedder):
    """Deterministic hash-based pseudo-embedder.

    Produces consistent 1024-dimensional float32 unit vectors.
    Useful for offline development, CI, and fast integration tests without downloading heavy weights.
    """

    def __init__(self, dim: int = 1024, model_name: str = "stub-bge-m3"):
        self._dim = dim
        self._model_name = model_name

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model_name

    def _hash_vector(self, text: str) -> np.ndarray:
        # Use hashlib sha256 as deterministic random seed
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Seed NumPy PRNG deterministically
        seed = int.from_bytes(h[:4], "big")
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self._dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)
        vectors = [self._hash_vector(t) for t in texts]
        return np.vstack(vectors)

    def embed_query(self, query: str) -> np.ndarray:
        return self._hash_vector(query)


class SentenceTransformerEmbedder(BaseEmbedder):
    """Embedder using sentence-transformers (BAAI/bge-m3)."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        dim: int = 1024,
        batch_size: int = 16,
        device: str = "cpu",
    ):
        self._model_name = model_name
        self._dim = dim
        self._batch_size = batch_size
        self._device = device
        self._model: Any = None

    def _load_model(self):
        if self._model is None:
            logger.info("Loading embedding model %s on %s...", self._model_name, self._device)
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name, device=self._device)
            logger.info("Embedding model loaded.")

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)
        self._load_model()
        vectors = self._model.encode(
            texts,
            batch_size=self._batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        self._load_model()
        vec = self._model.encode(
            query,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vec, dtype=np.float32)


# Singleton embedder instance
_embedder_instance: BaseEmbedder | None = None


def get_embedder() -> BaseEmbedder:
    """Get or initialize the configured embedder instance."""
    global _embedder_instance
    if _embedder_instance is None:
        settings = get_settings()
        try:
            import sentence_transformers  # noqa
            _embedder_instance = SentenceTransformerEmbedder(
                model_name=settings.embedding_model,
                dim=settings.embedding_dim,
                batch_size=settings.embedding_batch_size,
                device="cpu" if settings.embedding_device == "auto" else settings.embedding_device,
            )
        except ImportError:
            logger.info("sentence_transformers not installed; falling back to StubEmbedder.")
            _embedder_instance = StubEmbedder(
                dim=settings.embedding_dim,
                model_name=settings.embedding_model,
            )

    return _embedder_instance
