"""
Evidence selection & sufficiency gate — 03 §11, 05 §5.6.
Applies threshold sufficiency gate, diversity selection per paper,
token budget enforcement, and numbered source assignment.
"""

import logging
from typing import Any

from app.config import get_settings
from app.schemas.retrieval import SourceItem

logger = logging.getLogger("rgf.retrieval.evidence_selector")


def select_evidence(
    candidates: list[dict[str, Any]],
    min_evidence_chunks: int = 2,
    rerank_min_score: float = 0.20,
    max_chunks_per_paper: int = 3,
    context_max_tokens: int = 6000,
) -> tuple[list[SourceItem], bool]:
    """Apply sufficiency gate and evidence selection over reranked candidates.

    Returns:
        tuple of (selected_sources, insufficient_evidence_flag).
    """
    if not candidates:
        return [], True

    # 1. Sufficiency Gate (03 §11)
    highest_score = max(c.get("final_score", 0.0) for c in candidates)
    if len(candidates) < min_evidence_chunks or highest_score < rerank_min_score:
        logger.info(
            "Sufficiency gate failed: candidates=%d (min %d), top_score=%.3f (min %.3f)",
            len(candidates),
            min_evidence_chunks,
            highest_score,
            rerank_min_score,
        )
        return [], True

    # 2. Diversity & token budget selection
    paper_counts: dict[str, int] = {}
    accumulated_tokens = 0
    selected: list[SourceItem] = []

    for c in candidates:
        p_id = c.get("paper_id", "")
        if paper_counts.get(p_id, 0) >= max_chunks_per_paper:
            continue

        c_tokens = c.get("token_count", 0)
        if accumulated_tokens + c_tokens > context_max_tokens and selected:
            break

        paper_counts[p_id] = paper_counts.get(p_id, 0) + 1
        accumulated_tokens += c_tokens

        source_idx = len(selected) + 1
        selected.append(
            SourceItem(
                source_id=source_idx,
                paper_id=p_id,
                paper_title=c.get("title", ""),
                authors=c.get("authors", []),
                year=c.get("year"),
                page=c.get("page", 1),
                section=c.get("chunk_type", "OTHER"),
                section_heading=c.get("section_heading"),
                chunk_id=c.get("chunk_id", ""),
                text=c.get("text", ""),
                score=round(c.get("final_score", 0.0), 3),
            )
        )

    if len(selected) < min_evidence_chunks:
        return [], True

    return selected, False
