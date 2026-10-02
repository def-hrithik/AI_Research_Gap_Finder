"""
Section detector — 03 §3, 08 §14.
Combines typography (font size, bold) and lexical heading matching
against the canonical ChunkType synonym table.
"""

from collections import Counter
import logging
import re
from typing import NamedTuple

from app.ingestion.pdf_parser import ParsedPDF, TextBlock
from app.schemas.chunk import Paragraph, Section

logger = logging.getLogger("rgf.ingestion.section")

# Future work cue regex (03 §3)
FUTURE_CUE_RE = re.compile(
    r"\b(future work|future research|we plan to|remains to be|further investigation|would be interesting)\b",
    re.IGNORECASE,
)

# Limitation cue regex (03 §3)
LIMITATION_CUE_RE = re.compile(
    r"\b(limitation|however, our|does not generalize|we did not|restricted to|small sample)\b",
    re.IGNORECASE,
)

# Numbering prefix regex (e.g., "1.", "1.2", "IV.", "A.")
SECTION_NUMBER_RE = re.compile(
    r"^\s*([0-9]+(\.[0-9]+)*\.?|[IVXLCDM]+\.?|[A-Z]\.?)\s+",
    re.IGNORECASE,
)

# Canonical mapping table: order matters (first match wins)
CANONICAL_SYNONYMS: list[tuple[str, list[str]]] = [
    ("ABSTRACT", ["abstract", "summary"]),
    (
        "LIMITATION",
        [
            "limitation",
            "limitations",
            "threats to validity",
            "shortcoming",
            "shortcomings",
            "weaknesses",
        ],
    ),
    (
        "CONCLUSION",
        [
            "conclusion",
            "conclusions",
            "concluding remarks",
            "summary and conclusion",
            "conclusion and future work",
            "conclusions and future work",
        ],
    ),
    (
        "FUTURE_WORK",
        [
            "future work",
            "future directions",
            "future research",
            "outlook",
            "open problems",
            "open challenges",
        ],
    ),
    (
        "DATASET",
        [
            "dataset",
            "datasets",
            "data collection",
            "corpus",
            "benchmark",
            "benchmarks",
            "materials",
        ],
    ),
    (
        "METHODOLOGY",
        [
            "method",
            "methods",
            "methodology",
            "approach",
            "proposed method",
            "proposed approach",
            "proposed model",
            "proposed framework",
            "model architecture",
            "system design",
            "experimental setup",
            "implementation details",
            "training details",
            "evaluation protocol",
            "system architecture",
        ],
    ),
    (
        "RESULTS",
        [
            "results",
            "experiments",
            "experimental results",
            "evaluation",
            "findings",
            "performance analysis",
            "ablation",
            "ablations",
            "ablation study",
        ],
    ),
    (
        "DISCUSSION",
        ["discussion", "analysis", "interpretation", "implications"],
    ),
    (
        "RELATED_WORK",
        [
            "related work",
            "literature review",
            "prior work",
            "state of the art",
            "background and related work",
        ],
    ),
    (
        "INTRODUCTION",
        ["introduction", "background", "motivation", "problem statement"],
    ),
    (
        "REFERENCES",
        ["references", "bibliography"],
    ),
    (
        "OTHER",
        [
            "acknowledgement",
            "acknowledgements",
            "acknowledgments",
            "appendix",
            "appendices",
        ],
    ),
]


def strip_numbering(heading: str) -> tuple[str, int]:
    """Strip section numbering and return (stripped_text, numbering_depth).

    Examples:
        "1. Introduction" -> ("Introduction", 1)
        "3.2.1 Experimental Setup" -> ("Experimental Setup", 3)
        "Abstract" -> ("Abstract", 0)
    """
    match = SECTION_NUMBER_RE.match(heading)
    if not match:
        return heading.strip(), 0

    prefix = match.group(1).rstrip(".")
    depth = len(prefix.split(".")) if "." in prefix else 1
    stripped = heading[match.end():].strip()
    return stripped, depth


def match_canonical_chunk_type(heading_text: str, page: int = 1) -> str | None:
    """Match a heading against the canonical ChunkType table."""
    clean, _ = strip_numbering(heading_text)
    clean_lower = clean.lower()

    # Abstract only on page 1
    if page > 2 and ("abstract" in clean_lower or "summary" == clean_lower):
        return None

    for chunk_type, synonyms in CANONICAL_SYNONYMS:
        for syn in synonyms:
            # Check exact match or word-bounded match
            pattern = r"(^|\b)" + re.escape(syn) + r"(\b|$)"
            if re.search(pattern, clean_lower):
                return chunk_type

    return None


def calculate_body_font_size(parsed_pdf: ParsedPDF) -> float:
    """Calculate the median body font size weighted by characters."""
    font_char_counts: Counter[float] = Counter()
    for block in parsed_pdf.all_blocks:
        if not block.is_table and block.text.strip():
            # Round font size to nearest 0.5 pt
            rounded = round(block.font_size * 2) / 2.0
            font_char_counts[rounded] += len(block.text)

    if not font_char_counts:
        return 10.0

    return font_char_counts.most_common(1)[0][0]


def is_heading_candidate(block: TextBlock, body_font_size: float) -> bool:
    """Check if a block qualifies as a heading candidate.

    03 §3: (size >= 1.1x body OR bold) AND length <= 120 chars AND no terminal period AND not a caption.
    """
    if block.is_table or block.is_caption:
        return False

    text = block.text.strip()
    if not text or len(text) > 120 or len(text) < 2:
        return False

    # No terminal period (headings rarely end in a period, except e.g. "1. Introduction")
    # If it ends in a period, make sure it's not a full sentence
    clean, _ = strip_numbering(text)
    if clean.endswith(".") and not clean.endswith(".."):
        return False

    is_larger = block.font_size >= (1.08 * body_font_size)
    is_bold = block.is_bold

    return is_larger or is_bold


class SectionDetectionResult(NamedTuple):
    sections: list[Section]
    quality: str  # "high" | "low"


def detect_sections(parsed_pdf: ParsedPDF) -> SectionDetectionResult:
    """Detect canonical sections across all pages of a parsed PDF.

    Returns:
        SectionDetectionResult containing sections and quality flag ("high" or "low").
    """
    body_font_size = calculate_body_font_size(parsed_pdf)
    all_blocks = parsed_pdf.all_blocks

    # First pass: find candidate heading blocks and map their chunk types
    type_sections: list[tuple[str, str, int, list[TextBlock]]] = []
    # (heading_text, chunk_type, start_page, blocks)

    current_heading = "Header"
    current_type = "OTHER"
    current_page = 1
    current_blocks: list[TextBlock] = []
    headings_found = 0

    # Check if first page top block is an Abstract without a heading
    first_block = all_blocks[0] if all_blocks else None
    if first_block and first_block.page == 1 and first_block.text.strip().lower().startswith("abstract"):
        current_heading = "Abstract"
        current_type = "ABSTRACT"
        headings_found += 1

    for block in all_blocks:
        text = block.text.strip()
        if not text:
            continue

        if is_heading_candidate(block, body_font_size):
            matched_type = match_canonical_chunk_type(text, page=block.page)
            if matched_type is not None:
                # Flush previous section
                if current_blocks:
                    type_sections.append(
                        (current_heading, current_type, current_page, current_blocks)
                    )
                    current_blocks = []

                current_heading = text
                current_type = matched_type
                current_page = block.page
                headings_found += 1
                continue
            else:
                # Check subheading depth inheritance
                _, depth = strip_numbering(text)
                if depth > 1:
                    # Inherit previous section type
                    if current_blocks:
                        type_sections.append(
                            (current_heading, current_type, current_page, current_blocks)
                        )
                        current_blocks = []
                    current_heading = text
                    # current_type remains what it was
                    current_page = block.page
                    headings_found += 1
                    continue

        current_blocks.append(block)

    if current_blocks:
        type_sections.append(
            (current_heading, current_type, current_page, current_blocks)
        )

    # Fallback if insufficient headings detected (quality = "low")
    quality = "high"
    if headings_found < 2:
        quality = "low"
        logger.warning(
            "Low section detection quality (%d headings found). Using fallback.",
            headings_found,
        )
        if not type_sections:
            # Create a single default section
            type_sections = [("Full Document", "OTHER", 1, all_blocks)]

    # Build final Section objects with paragraph grouping and cue tagging
    final_sections: list[Section] = []

    for heading, chunk_type, start_page, blocks in type_sections:
        if not blocks:
            continue

        paragraphs: list[Paragraph] = []
        has_future_cue = False
        has_limitation_cue = False
        page_end = start_page

        for b in blocks:
            b_text = b.text.strip()
            if not b_text:
                continue

            page_end = max(page_end, b.page)

            # Check for cue words
            if FUTURE_CUE_RE.search(b_text):
                has_future_cue = True
            if LIMITATION_CUE_RE.search(b_text):
                has_limitation_cue = True

            paragraphs.append(
                Paragraph(
                    text=b_text,
                    page=b.page,
                    is_table=b.is_table,
                )
            )

        final_sections.append(
            Section(
                heading=heading,
                chunk_type=chunk_type,
                page_start=start_page,
                page_end=page_end,
                paragraphs=paragraphs,
                has_future_cue=has_future_cue,
                has_limitation_cue=has_limitation_cue,
            )
        )

    return SectionDetectionResult(sections=final_sections, quality=quality)
