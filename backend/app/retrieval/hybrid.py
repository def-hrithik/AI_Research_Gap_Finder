"""
Hybrid retrieval pipeline — 03 §8–11.
Combines Dense search (Qdrant) and Lexical search (BM25) via RRF,
applies intent-driven section priors, cross-encoder reranking, and sufficiency gating.
"""

from collections import defaultdict
import logging
import time
from typing import Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import repos
from app.database.qdrant import get_vector_store
from app.embeddings.embedder import get_embedder
from app.retrieval.bm25 import search_bm25
from app.retrieval.evidence_selector import select_evidence
from app.retrieval.intent import detect_intent, get_section_boost
from app.retrieval.reranker import get_reranker
from app.schemas.retrieval import SearchFilters, SourceItem

logger = logging.getLogger("rgf.retrieval.hybrid")


def rrf_fuse(
    dense_results: list[dict[str, Any]],
    bm25_results: list[tuple[str, float]],
    k: int = 60,
) -> list[dict[str, Any]]:
    """Compute Reciprocal Rank Fusion (03 §9).

    score(d) = sum(1 / (k + rank_r(d)))
    """
    fused_scores: dict[str, float] = defaultdict(float)
    chunk_data: dict[str, dict[str, Any]] = {}

    # Dense ranks (1-indexed)
    for rank_idx, item in enumerate(dense_results):
        c_id = item["chunk_id"]
        dense_rank = rank_idx + 1
        fused_scores[c_id] += 1.0 / (k + dense_rank)

        chunk_data[c_id] = dict(item.get("payload", {}))
        chunk_data[c_id]["dense_score"] = item.get("score")
        chunk_data[c_id]["dense_rank"] = dense_rank

    # BM25 ranks (1-indexed)
    for rank_idx, (c_id, score) in enumerate(bm25_results):
        bm25_rank = rank_idx + 1
        fused_scores[c_id] += 1.0 / (k + bm25_rank)

        if c_id not in chunk_data:
            chunk_data[c_id] = {"chunk_id": c_id}
        chunk_data[c_id]["bm25_score"] = score
        chunk_data[c_id]["bm25_rank"] = bm25_rank

    if not fused_scores:
        return []

    # Normalize by max RRF score (03 §9)
    max_rrf = max(fused_scores.values())

    candidates: list[dict[str, Any]] = []
    for c_id, raw_rrf in fused_scores.items():
        norm_rrf = raw_rrf / max_rrf if max_rrf > 0 else 0.0
        data = chunk_data.get(c_id, {})
        data["chunk_id"] = c_id
        data["rrf_score"] = norm_rrf
        candidates.append(data)

    return candidates


class HybridRetriever:
    """End-to-end hybrid retrieval engine."""

    def __init__(self):
        self.settings = get_settings()

    def retrieve(
        self,
        project_id: str,
        query: str,
        db: Session,
        filters: SearchFilters | None = None,
        top_k: int = 10,
    ) -> tuple[list[SourceItem], bool, str, dict[str, Any]]:
        """Execute the full retrieval pipeline:
        Intent → Dense + BM25 → RRF → Section Prior → Rerank → Gate & Select.

        Returns:
            tuple of (sources, insufficient_evidence, intent_name, stats_dict).
        """
        start_time = time.perf_counter()
        timings: dict[str, int] = {}

        paper_ids = filters.paper_ids if filters else None
        chunk_types = filters.chunk_types if filters else None

        # 1. Intent Detection & Section Prior
        t0 = time.perf_counter()
        primary_intent, intent_prior = detect_intent(query)
        timings["intent_ms"] = int((time.perf_counter() - t0) * 1000)

        # 2. Dense Vector Search (Qdrant)
        t0 = time.perf_counter()
        embedder = get_embedder()
        q_vec = embedder.embed_query(query)

        vs = get_vector_store()
        dense_results = vs.search(
            project_id=project_id,
            query_vector=q_vec,
            top_k=self.settings.retrieval_dense_top_k,
            paper_ids=paper_ids,
            chunk_types=chunk_types,
        )
        timings["dense_ms"] = int((time.perf_counter() - t0) * 1000)

        # 3. Lexical Search (BM25)
        t0 = time.perf_counter()
        bm25_results = search_bm25(
            project_id=project_id,
            query=query,
            db=db,
            top_k=self.settings.retrieval_bm25_top_k,
            paper_ids=paper_ids,
            chunk_types=chunk_types,
        )
        timings["bm25_ms"] = int((time.perf_counter() - t0) * 1000)

        # Populate missing chunk payload details from SQLite for BM25-only hits
        for c_id, _ in bm25_results:
            if not any(d.get("chunk_id") == c_id for d in dense_results):
                chunk_obj = repos.get_chunk(db, c_id)
                if chunk_obj:
                    paper = chunk_obj.paper
                    dense_results.append({
                        "chunk_id": c_id,
                        "score": 0.0,
                        "payload": {
                            "chunk_id": chunk_obj.chunk_id,
                            "paper_id": chunk_obj.paper_id,
                            "project_id": chunk_obj.project_id,
                            "title": paper.title if paper else "",
                            "authors": paper.authors if paper else [],
                            "year": paper.year if paper else None,
                            "section_heading": chunk_obj.section_heading,
                            "chunk_type": chunk_obj.chunk_type,
                            "page": chunk_obj.page,
                            "page_end": chunk_obj.page_end,
                            "chunk_index": chunk_obj.chunk_index,
                            "is_table": chunk_obj.is_table,
                            "has_future_cue": chunk_obj.has_future_cue,
                            "has_limitation_cue": chunk_obj.has_limitation_cue,
                            "text": chunk_obj.text,
                            "token_count": chunk_obj.token_count,
                        },
                    })

        # 4. RRF Fusion
        t0 = time.perf_counter()
        candidates = rrf_fuse(dense_results, bm25_results, k=self.settings.rrf_k)

        # Apply section prior boost
        for c in candidates:
            boost = get_section_boost(
                chunk_type=c.get("chunk_type", "OTHER"),
                has_limitation_cue=c.get("has_limitation_cue", False),
                has_future_cue=c.get("has_future_cue", False),
                intent_prior=intent_prior,
                primary_intent=primary_intent,
            )
            c["section_boost"] = boost
            c["prior_score"] = c.get("rrf_score", 0.0) + boost

        # Sort by prior_score and take top rerank candidates (50)
        candidates.sort(key=lambda x: x["prior_score"], reverse=True)
        candidates = candidates[: self.settings.rerank_candidates]
        timings["fusion_ms"] = int((time.perf_counter() - t0) * 1000)

        # 5. Cross-Encoder Reranking
        t0 = time.perf_counter()
        reranker = get_reranker()
        reranked = reranker.rerank(query, candidates, top_k=self.settings.rerank_top_k)
        timings["rerank_ms"] = int((time.perf_counter() - t0) * 1000)

        # 6. Sufficiency Gate & Evidence Selection
        t0 = time.perf_counter()
        sources, insufficient_evidence = select_evidence(
            candidates=reranked,
            min_evidence_chunks=self.settings.min_evidence_chunks,
            rerank_min_score=self.settings.rerank_min_score,
            max_chunks_per_paper=self.settings.max_chunks_per_paper,
            context_max_tokens=self.settings.context_max_tokens,
        )
        timings["select_ms"] = int((time.perf_counter() - t0) * 1000)

        total_latency = int((time.perf_counter() - start_time) * 1000)
        timings["total_latency_ms"] = total_latency

        stats = {
            "timings": timings,
            "dense_count": len(dense_results),
            "bm25_count": len(bm25_results),
            "candidates_count": len(candidates),
            "sources_count": len(sources),
        }

        return sources, insufficient_evidence, primary_intent, stats


# Global retriever instance
_retriever: HybridRetriever | None = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever
