"""
Retrieval and Search schemas — 03 §8–14, 05 §5.6, 06 §8.
"""

from typing import Any
from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    paper_ids: list[str] | None = None
    chunk_types: list[str] | None = None
    year_from: int | None = None
    year_to: int | None = None


class SearchRequest(BaseModel):
    project_id: str
    query: str
    filters: SearchFilters | None = None
    generate_answer: bool = True
    top_k: int = 10


class ScoredChunk(BaseModel):
    chunk_id: str
    paper_id: str
    project_id: str
    title: str
    authors: list[str] = []
    year: int | None = None
    section_heading: str | None = None
    chunk_type: str
    page: int
    page_end: int
    chunk_index: int
    text: str
    token_count: int
    is_table: bool = False
    has_future_cue: bool = False
    has_limitation_cue: bool = False
    dense_score: float | None = None
    dense_rank: int | None = None
    bm25_score: float | None = None
    bm25_rank: int | None = None
    rrf_score: float = 0.0
    prior_score: float = 0.0
    rerank_score: float | None = None
    final_score: float = 0.0


class SourceItem(BaseModel):
    """Response-level citation source — 05 §5.6."""
    source_id: int
    paper_id: str
    paper_title: str
    authors: list[str] = []
    year: int | None = None
    page: int
    section: str
    section_heading: str | None = None
    chunk_id: str
    text: str
    score: float


class SearchResponse(BaseModel):
    """POST /api/search response — 06 §8."""
    query: str
    intent: str
    answer: str
    sources: list[SourceItem] = []
    insufficient_evidence: bool = False
    stats: dict[str, Any] = Field(default_factory=dict)
