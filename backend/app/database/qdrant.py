"""
Qdrant vector store adapter — 03 §6, 05 §5.4.
Manages collection lifecycle, point indexing, and project-isolated vector search.
"""

import logging
from pathlib import Path
from typing import Any
import uuid
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import get_settings
from app.core.constants import QDRANT_UUID_NAMESPACE
from app.core.errors import VectorStoreError
from app.schemas.chunk import ChunkResponse

logger = logging.getLogger("rgf.database.qdrant")

# Constant UUID namespace for deterministic point IDs
_NAMESPACE_UUID = uuid.uuid5(uuid.NAMESPACE_DNS, QDRANT_UUID_NAMESPACE)


def chunk_id_to_point_id(chunk_id: str) -> str:
    """Generate a valid deterministic UUID string for Qdrant from chunk_id (03 §6)."""
    return str(uuid.uuid5(_NAMESPACE_UUID, chunk_id))


class QdrantVectorStore:
    """Manages Qdrant client connection and vector operations."""

    def __init__(self):
        settings = get_settings()
        self.collection_name = settings.qdrant_collection
        self.embedding_dim = settings.embedding_dim

        try:
            if settings.qdrant_url:
                self.client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key or None,
                )
                logger.info("Connected to remote Qdrant at %s", settings.qdrant_url)
            else:
                # Embedded local path mode (03 §6)
                local_path = Path(settings.qdrant_local_path)
                local_path.mkdir(parents=True, exist_ok=True)
                self.client = QdrantClient(path=str(local_path))
                logger.info("Initialized local embedded Qdrant at %s", local_path)

            self._ensure_collection()
        except Exception as exc:
            logger.exception("Failed to initialize Qdrant vector store: %s", exc)
            raise VectorStoreError(f"Failed to connect to Qdrant: {str(exc)}")

    def _ensure_collection(self) -> None:
        """Create collection and payload indexes if they do not already exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                logger.info(
                    "Creating Qdrant collection '%s' (dim=%d, cosine)",
                    self.collection_name,
                    self.embedding_dim,
                )
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.embedding_dim,
                        distance=qmodels.Distance.COSINE,
                    ),
                )

                # Create payload indexes (03 §6)
                for field, schema in [
                    ("project_id", qmodels.PayloadSchemaType.KEYWORD),
                    ("paper_id", qmodels.PayloadSchemaType.KEYWORD),
                    ("chunk_type", qmodels.PayloadSchemaType.KEYWORD),
                    ("year", qmodels.PayloadSchemaType.INTEGER),
                ]:
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name=field,
                            field_schema=schema,
                        )
                    except Exception as e:
                        logger.debug("Payload index creation note: %s", e)
        except Exception as exc:
            logger.warning("Qdrant collection verification encountered: %s", exc)

    def upsert_chunks(
        self,
        chunks: list[ChunkResponse],
        vectors: np.ndarray,
        source_filename: str = "",
    ) -> None:
        """Upsert embedded chunks into Qdrant collection."""
        if not chunks:
            return

        points: list[qmodels.PointStruct] = []
        for i, chunk in enumerate(chunks):
            point_id = chunk_id_to_point_id(chunk.chunk_id)
            vector_list = vectors[i].tolist()

            payload = {
                "chunk_id": chunk.chunk_id,
                "paper_id": chunk.paper_id,
                "project_id": chunk.project_id,
                "title": chunk.title,
                "authors": chunk.authors,
                "year": chunk.year,
                "section_heading": chunk.section_heading,
                "chunk_type": chunk.chunk_type,
                "page": chunk.page,
                "page_end": chunk.page_end,
                "chunk_index": chunk.chunk_index,
                "is_table": chunk.is_table,
                "has_future_cue": chunk.has_future_cue,
                "has_limitation_cue": chunk.has_limitation_cue,
                "text": chunk.text,
                "token_count": chunk.token_count,
                "source_filename": source_filename,
            }

            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector_list,
                    payload=payload,
                )
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )
            logger.info("Upserted %d points to Qdrant collection '%s'", len(points), self.collection_name)
        except Exception as exc:
            logger.exception("Failed to upsert points to Qdrant: %s", exc)
            raise VectorStoreError(f"Vector store upsert failed: {str(exc)}")

    def search(
        self,
        project_id: str,
        query_vector: np.ndarray,
        top_k: int = 40,
        paper_ids: list[str] | None = None,
        chunk_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search vector collection with mandatory project_id isolation (03 §6)."""
        # Build filter must: project_id == project_id
        must_conditions: list[qmodels.Condition] = [
            qmodels.FieldCondition(
                key="project_id",
                match=qmodels.MatchValue(value=project_id),
            )
        ]

        if paper_ids:
            must_conditions.append(
                qmodels.FieldCondition(
                    key="paper_id",
                    match=qmodels.MatchAny(any=paper_ids),
                )
            )

        if chunk_types:
            must_conditions.append(
                qmodels.FieldCondition(
                    key="chunk_type",
                    match=qmodels.MatchAny(any=chunk_types),
                )
            )

        filter_query = qmodels.Filter(must=must_conditions)

        try:
            vec_list = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=vec_list,
                    query_filter=filter_query,
                    limit=top_k,
                    with_payload=True,
                )
                results = response.points
            else:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=vec_list,
                    query_filter=filter_query,
                    limit=top_k,
                    with_payload=True,
                )

            scored_items = []
            for r in results:
                payload = r.payload or {}
                scored_items.append({
                    "chunk_id": payload.get("chunk_id", ""),
                    "score": float(r.score),
                    "payload": payload,
                })
            return scored_items

        except Exception as exc:
            logger.exception("Qdrant vector search failed: %s", exc)
            raise VectorStoreError(f"Vector search failed: {str(exc)}")

    def delete_by_paper(self, paper_id: str) -> None:
        """Delete all points belonging to a specific paper (03 §6)."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="paper_id",
                                match=qmodels.MatchValue(value=paper_id),
                            )
                        ]
                    )
                ),
                wait=True,
            )
            logger.info("Deleted vector points for paper %s", paper_id)
        except Exception as exc:
            logger.warning("Error deleting vectors for paper %s: %s", paper_id, exc)

    def count(self, project_id: str | None = None) -> int:
        """Count points in the collection, optionally filtered by project_id."""
        try:
            count_filter = None
            if project_id:
                count_filter = qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="project_id",
                            match=qmodels.MatchValue(value=project_id),
                        )
                    ]
                )
            res = self.client.count(
                collection_name=self.collection_name,
                count_filter=count_filter,
                exact=True,
            )
            return res.count
        except Exception:
            return 0


# Singleton vector store instance
_vector_store: QdrantVectorStore | None = None


def get_vector_store() -> QdrantVectorStore:
    """Get or initialize singleton Qdrant vector store."""
    global _vector_store
    if _vector_store is None:
        _vector_store = QdrantVectorStore()
    return _vector_store
