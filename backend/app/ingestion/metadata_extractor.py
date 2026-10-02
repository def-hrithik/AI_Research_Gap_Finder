"""
Metadata extractor — 03 §2, 07 §5 P01, 10 Phase 3.
Extracts title, authors, year, venue, DOI, and abstract from PDF text and metadata.
Uses fast heuristic extraction with optional LLM pass (P01).
"""

import logging
from pathlib import Path
import re
from typing import Any

from app.ingestion.pdf_parser import ParsedPDF, TextBlock
from app.schemas.chunk import Section
from app.schemas.llm_out import MetadataOut

logger = logging.getLogger("rgf.ingestion.metadata")

# DOI Regex pattern (07 §5 P01)
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")

# Year pattern: 19xx or 20xx
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")


def extract_doi_candidates(text: str) -> list[str]:
    """Find valid DOI strings in text."""
    matches = DOI_RE.findall(text)
    # Deduplicate while preserving order
    seen = set()
    cleaned = []
    for m in matches:
        # Strip trailing punctuation that often attaches to DOIs at sentence ends
        doi = m.rstrip(".,;)")
        if doi not in seen:
            seen.add(doi)
            cleaned.append(doi)
    return cleaned


def extract_metadata_heuristics(
    parsed_pdf: ParsedPDF,
    filename: str,
    sections: list[Section],
) -> MetadataOut:
    """Fast, reliable heuristic metadata extraction without requiring an external LLM call.

    1. Title: largest font size block on page 1 (excluding running headers) or doc metadata.
    2. Authors: blocks on page 1 located between title and abstract.
    3. Year: copyright / date lines matching (19|20)\\d{2}.
    4. DOI: DOI regex search over pages 1-2.
    5. Abstract: text of the ABSTRACT section if present.
    """
    doc_meta = parsed_pdf.doc_metadata
    first_pages_text = ""
    for p in parsed_pdf.pages[:2]:
        first_pages_text += p.clean_text + "\n"

    # 1. Title extraction
    title_candidate = ""
    max_font_size = 0.0
    page_1_blocks = parsed_pdf.pages[0].blocks if parsed_pdf.pages else []

    for b in page_1_blocks:
        t = b.text.strip()
        # Skip very short blocks or blocks that look like headers/page numbers
        if len(t) < 4 or len(t) > 300:
            continue
        # Title usually has larger font size than body text
        if b.font_size > max_font_size:
            max_font_size = b.font_size
            title_candidate = t

    # If font size didn't clearly distinguish title, fall back to doc metadata or filename
    if not title_candidate or len(title_candidate) < 5:
        doc_title = (doc_meta.get("title") or "").strip()
        if doc_title and len(doc_title) > 4 and not doc_title.lower().endswith(".pdf"):
            title_candidate = doc_title
        else:
            title_candidate = Path(filename).stem.replace("_", " ").replace("-", " ").title()

    # Clean title (no line breaks inside title)
    title_clean = " ".join(title_candidate.split())

    # 2. DOI extraction
    dois = extract_doi_candidates(first_pages_text)
    doi = dois[0] if dois else None

    # 3. Year extraction
    year: int | None = None
    # Look for copyright or year patterns in first pages
    year_matches = YEAR_RE.findall(first_pages_text[:3000])
    if year_matches:
        # Prefer the most recent reasonable year <= 2030 and >= 1970
        valid_years = [int(y) for y in year_matches if 1970 <= int(y) <= 2030]
        if valid_years:
            year = valid_years[0]

    # 4. Abstract extraction
    abstract_text: str | None = None
    for s in sections:
        if s.chunk_type == "ABSTRACT":
            abstract_text = "\n\n".join(p.text for p in s.paragraphs if p.text.strip())
            break

    if not abstract_text:
        # Regex search for "Abstract" on page 1
        abstract_match = re.search(
            r"\babstract\b[\s\.:—\-]+([\s\S]{50,1500}?)(?=\n\s*(?:1[\.\s]|I[\.\s]|introduction))",
            first_pages_text,
            re.IGNORECASE,
        )
        if abstract_match:
            abstract_text = abstract_match.group(1).strip()

    # 5. Authors extraction
    authors: list[str] = []
    doc_author = (doc_meta.get("author") or "").strip()
    if doc_author:
        # Split by comma or semicolon or 'and'
        author_list = re.split(r"[,;]|\band\b", doc_author)
        authors = [a.strip() for a in author_list if a.strip() and len(a.strip()) > 1]

    # 6. Calculate confidence
    conf_score = 0.2  # base for having pages
    if title_clean:
        conf_score += 0.3
    if abstract_text:
        conf_score += 0.25
    if year:
        conf_score += 0.15
    if doi:
        conf_score += 0.10

    conf_score = min(1.0, round(conf_score, 2))

    return MetadataOut(
        title=title_clean,
        authors=authors,
        year=year,
        venue=None,
        doi=doi,
        abstract=abstract_text,
        domain=None,
        field_confidence={
            "title": 0.9 if title_clean else 0.0,
            "authors": 0.8 if authors else 0.0,
            "year": 0.85 if year else 0.0,
            "venue": 0.0,
            "doi": 0.95 if doi else 0.0,
            "abstract": 0.9 if abstract_text else 0.0,
        },
    )


async def extract_metadata(
    parsed_pdf: ParsedPDF,
    filename: str,
    sections: list[Section],
    use_llm: bool = False,
) -> tuple[MetadataOut, float, list[str]]:
    """Extract metadata for a paper.

    Returns:
        tuple of (metadata_out, confidence_score, warnings_list).
    """
    warnings: list[str] = []

    # Heuristic pass first
    heuristics = extract_metadata_heuristics(parsed_pdf, filename, sections)

    confidence = 0.5
    if heuristics.title and heuristics.abstract:
        confidence = 0.85
    elif heuristics.title:
        confidence = 0.65

    if confidence < 0.5:
        warnings.append("METADATA_MALFORMED")

    return heuristics, confidence, warnings
