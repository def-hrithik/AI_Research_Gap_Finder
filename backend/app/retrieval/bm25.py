"""
Lexical search via BM25 — 03 §7.
Per-project BM25Okapi index with technical-term preserving tokenization
and LRU caching.
"""

from collections import OrderedDict
import logging
import re
from typing import Any
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import repos
from app.database.session import get_session

logger = logging.getLogger("rgf.retrieval.bm25")

# Tokenizer pattern keeping technical terms: BERT-base, F1, 3.5, etc.
TOKEN_PATTERN = re.compile(r"\b[\w\-\+\.]*\w\b", re.UNICODE)

# Common English stopwords (compact set to avoid external NLTK dependency)
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves",
}


def tokenize_bm25(text: str) -> list[str]:
    """Tokenize technical academic text: preserves hyphens/dots in terms, strips stopwords."""
    tokens = TOKEN_PATTERN.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


class ProjectBM25Index:
    """In-memory BM25 index for a single project's chunks."""

    def __init__(self, chunks: list[Any]):
        self.chunk_ids = [c.chunk_id for c in chunks]
        self.chunks_map = {c.chunk_id: c for c in chunks}
        corpus_tokens = [tokenize_bm25(f"{c.section_heading or ''} {c.text}") for c in chunks]
        self.bm25 = BM25Okapi(corpus_tokens, k1=1.5, b=0.75) if corpus_tokens else None

    def search(
        self,
        query: str,
        top_k: int = 40,
        paper_ids: list[str] | None = None,
        chunk_types: list[str] | None = None,
    ) -> list[tuple[str, float]]:
        """Score all chunks, apply filters, and return top_k (chunk_id, score)."""
        if not self.bm25 or not self.chunk_ids:
            return []

        tokens = tokenize_bm25(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)

        results: list[tuple[str, float]] = []
        for idx, score in enumerate(scores):
            if score <= 0.0:
                continue

            c_id = self.chunk_ids[idx]
            chunk = self.chunks_map[c_id]

            if paper_ids and chunk.paper_id not in paper_ids:
                continue
            if chunk_types and chunk.chunk_type not in chunk_types:
                continue

            results.append((c_id, float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


# LRU Cache for BM25 indices: project_id -> ProjectBM25Index
_bm25_cache: OrderedDict[str, ProjectBM25Index] = OrderedDict()


def invalidate_project_bm25(project_id: str) -> None:
    """Invalidate cached BM25 index when a paper is uploaded or deleted."""
    _bm25_cache.pop(project_id, None)
    logger.debug("Invalidated BM25 index for project %s", project_id)


def get_project_bm25(project_id: str, db: Session) -> ProjectBM25Index:
    """Get or build the BM25 index for a project."""
    settings = get_settings()

    if project_id in _bm25_cache:
        _bm25_cache.move_to_end(project_id)
        return _bm25_cache[project_id]

    chunks = repos.list_chunks_by_project(db, project_id, exclude_references=True)
    idx = ProjectBM25Index(chunks)

    _bm25_cache[project_id] = idx
    while len(_bm25_cache) > settings.bm25_cache_projects:
        _bm25_cache.popitem(last=False)

    return idx


def search_bm25(
    project_id: str,
    query: str,
    db: Session,
    top_k: int = 40,
    paper_ids: list[str] | None = None,
    chunk_types: list[str] | None = None,
) -> list[tuple[str, float]]:
    """Execute BM25 search for a project."""
    index = get_project_bm25(project_id, db)
    return index.search(query, top_k=top_k, paper_ids=paper_ids, chunk_types=chunk_types)
