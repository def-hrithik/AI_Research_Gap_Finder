"""
Structure-aware chunker — 03 §4, 05 §5.3.
Splits sections into section-bounded, page-preserving chunks with deterministic IDs.
"""

import logging
import re
from typing import Any

from app.core.ids import chunk_id
from app.ingestion.section_detector import FUTURE_CUE_RE, LIMITATION_CUE_RE
from app.schemas.chunk import ChunkResponse, Paragraph, Section

logger = logging.getLogger("rgf.ingestion.chunker")

# Protected abbreviations so sentence splitter does not break on them
ABBREVIATIONS = [
    r"et al\.",
    r"Fig\.",
    r"Figs\.",
    r"e\.g\.",
    r"i\.e\.",
    r"vs\.",
    r"approx\.",
    r"ref\.",
    r"refs\.",
    r"sec\.",
    r"secs\.",
    r"eq\.",
    r"eqs\.",
    r"al\.",
    r"Dr\.",
    r"Prof\.",
    r"Vol\.",
    r"No\.",
    r"pp\.",
    r"cf\.",
]
PROTECTED_PATTERN = re.compile("|".join(ABBREVIATIONS), re.IGNORECASE)


def estimate_tokens(text: str) -> int:
    """Fast token estimation: words * 1.3 (03 §4)."""
    return max(1, int(len(text.split()) * 1.3))


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences while respecting common academic abbreviations."""
    # Temporarily replace protected abbreviations with placeholders
    placeholders: dict[str, str] = {}

    def replace_abbrev(match):
        key = f"__ABBR_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    masked = PROTECTED_PATTERN.sub(replace_abbrev, text)

    # Protect decimal numbers (e.g., 3.14, 0.95)
    masked = re.sub(r"(\d+)\.(\d+)", r"\1__DECIMAL__\2", masked)

    # Sentence boundary: period/question/exclamation followed by whitespace and uppercase or end of string
    raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\(\[\"\'])", masked)

    sentences: list[str] = []
    for s in raw_sentences:
        s = s.strip()
        if not s:
            continue
        # Restore decimals and abbreviations
        s = s.replace("__DECIMAL__", ".")
        for placeholder, original in placeholders.items():
            s = s.replace(placeholder, original)
        sentences.append(s)

    return sentences if sentences else [text]


def build_embedding_text(
    title: str,
    chunk_type: str,
    section_heading: str | None,
    text: str,
) -> str:
    """Build the contextual header embedding string (03 §4).

    Format: "{title} | {chunk_type} | {section_heading}\\n{text}"
    """
    heading = section_heading or chunk_type
    return f"{title} | {chunk_type} | {heading}\n{text}"


class Chunker:
    """Structure-aware chunker adhering to 03 §4."""

    def __init__(
        self,
        target_tokens: int = 350,
        max_tokens: int = 600,
        min_tokens: int = 60,
        overlap_sentences: int = 2,
    ):
        self.target_tokens = target_tokens
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.overlap_sentences = overlap_sentences

    def chunk_paper(
        self,
        paper_id: str,
        project_id: str,
        title: str,
        authors: list[str],
        year: int | None,
        sections: list[Section],
    ) -> list[ChunkResponse]:
        """Chunk all sections of a paper into discrete Chunk objects.

        Invariants:
        1. No chunk spans across two sections.
        2. Abstract is exactly one chunk (capped at 900 tokens).
        3. Table paragraphs become their own chunk with is_table=True.
        4. References section is excluded from standard retrieval chunks.
        5. Page provenance: page = first paragraph's page, page_end = last paragraph's page.
        6. Trailing chunks < min_tokens are merged into previous chunk within same section.
        """
        all_chunks: list[ChunkResponse] = []
        global_chunk_idx = 0

        for section in sections:
            # Skip references from retrieval chunks (03 §2, 03 §3)
            if section.chunk_type == "REFERENCES":
                continue

            # Special case 1: Abstract is exactly one chunk (03 §4: cap at 900 tokens)
            if section.chunk_type == "ABSTRACT":
                abstract_text = "\n\n".join(p.text for p in section.paragraphs if p.text.strip())
                if not abstract_text:
                    continue

                tok_count = estimate_tokens(abstract_text)
                c_id = chunk_id(paper_id, global_chunk_idx)
                all_chunks.append(
                    ChunkResponse(
                        chunk_id=c_id,
                        paper_id=paper_id,
                        project_id=project_id,
                        title=title,
                        authors=authors,
                        year=year,
                        section_heading=section.heading,
                        chunk_type="ABSTRACT",
                        page=section.page_start,
                        page_end=section.page_end,
                        chunk_index=global_chunk_idx,
                        text=abstract_text,
                        token_count=min(tok_count, 900),
                        is_table=False,
                        has_future_cue=bool(FUTURE_CUE_RE.search(abstract_text)),
                        has_limitation_cue=bool(LIMITATION_CUE_RE.search(abstract_text)),
                    )
                )
                global_chunk_idx += 1
                continue

            # Process paragraphs inside section
            section_chunks: list[dict[str, Any]] = []
            cur_sentences: list[str] = []
            cur_tokens = 0
            cur_start_page = section.page_start
            cur_end_page = section.page_start
            cur_is_table = False

            for para in section.paragraphs:
                p_text = para.text.strip()
                if not p_text:
                    continue

                # Table paragraphs get their own chunk (03 §4)
                if para.is_table:
                    # Flush current non-table sentences first
                    if cur_sentences:
                        s_text = " ".join(cur_sentences)
                        section_chunks.append({
                            "text": s_text,
                            "page": cur_start_page,
                            "page_end": cur_end_page,
                            "is_table": False,
                        })
                        cur_sentences = []
                        cur_tokens = 0

                    section_chunks.append({
                        "text": p_text,
                        "page": para.page,
                        "page_end": para.page,
                        "is_table": True,
                    })
                    continue

                # Normal paragraph: split into sentences
                sentences = split_into_sentences(p_text)

                for sent in sentences:
                    s_tokens = estimate_tokens(sent)

                    if cur_tokens + s_tokens > self.max_tokens and cur_sentences:
                        # Flush chunk
                        c_text = " ".join(cur_sentences)
                        section_chunks.append({
                            "text": c_text,
                            "page": cur_start_page,
                            "page_end": cur_end_page,
                            "is_table": False,
                        })

                        # Overlap: keep last `overlap_sentences`
                        if self.overlap_sentences > 0:
                            overlap = cur_sentences[-self.overlap_sentences:]
                            cur_sentences = list(overlap)
                            cur_tokens = sum(estimate_tokens(s) for s in cur_sentences)
                            # Start page remains where the overlap started
                        else:
                            cur_sentences = []
                            cur_tokens = 0
                            cur_start_page = para.page

                    if not cur_sentences:
                        cur_start_page = para.page

                    cur_sentences.append(sent)
                    cur_tokens += s_tokens
                    cur_end_page = para.page

            # Flush any remaining sentences in section
            if cur_sentences:
                c_text = " ".join(cur_sentences)
                section_chunks.append({
                    "text": c_text,
                    "page": cur_start_page,
                    "page_end": cur_end_page,
                    "is_table": False,
                })

            # Check trailing chunk: merge if < min_tokens and previous chunk has space
            if len(section_chunks) >= 2:
                last = section_chunks[-1]
                prev = section_chunks[-2]
                last_tokens = estimate_tokens(last["text"])
                prev_tokens = estimate_tokens(prev["text"])

                if not last["is_table"] and not prev["is_table"]:
                    if last_tokens < self.min_tokens or (last_tokens + prev_tokens <= self.max_tokens):
                        prev["text"] = prev["text"] + "\n\n" + last["text"]
                        prev["page_end"] = max(prev["page_end"], last["page_end"])
                        section_chunks.pop()

            # Create final ChunkResponse objects
            for sc in section_chunks:
                txt = sc["text"]
                toks = estimate_tokens(txt)
                c_id = chunk_id(paper_id, global_chunk_idx)
                all_chunks.append(
                    ChunkResponse(
                        chunk_id=c_id,
                        paper_id=paper_id,
                        project_id=project_id,
                        title=title,
                        authors=authors,
                        year=year,
                        section_heading=section.heading,
                        chunk_type=section.chunk_type,
                        page=sc["page"],
                        page_end=sc["page_end"],
                        chunk_index=global_chunk_idx,
                        text=txt,
                        token_count=toks,
                        is_table=sc["is_table"],
                        has_future_cue=bool(FUTURE_CUE_RE.search(txt)),
                        has_limitation_cue=bool(LIMITATION_CUE_RE.search(txt)),
                    )
                )
                global_chunk_idx += 1

        return all_chunks
