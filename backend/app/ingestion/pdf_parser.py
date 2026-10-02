"""
PDF parser using PyMuPDF (fitz) — 03 §2, 06 §1.4, 08 §14.
Extracts text with reading order (2-column aware), removes headers/footers,
extracts tables best-effort, and detects scanned/corrupt/oversized PDFs.
"""

from collections import Counter
import logging
from pathlib import Path
import re
import unicodedata
from typing import Any

import fitz  # PyMuPDF

from app.core.errors import IngestError
from app.core.text_normalize import dehyphenate

logger = logging.getLogger("rgf.ingestion.pdf")

# Regex to detect reference/bibliography heading
REF_HEADING_RE = re.compile(
    r"^\s*(\d+(\.\d+)*\.?|[IVX]+\.?)?\s*(references|bibliography)\s*$",
    re.IGNORECASE,
)

# Caption detection regex
CAPTION_RE = re.compile(r"^\s*(Figure|Fig\.|Table)\s+\d+[\.:]", re.IGNORECASE)


class TextBlock:
    """Represents an extracted text block with typography and bounding box."""

    def __init__(
        self,
        text: str,
        bbox: tuple[float, float, float, float],
        font_size: float = 10.0,
        is_bold: bool = False,
        page: int = 1,
        is_table: bool = False,
        is_caption: bool = False,
    ):
        self.text = text
        self.bbox = bbox  # (x0, y0, x1, y1)
        self.font_size = font_size
        self.is_bold = is_bold
        self.page = page
        self.is_table = is_table
        self.is_caption = is_caption

    @property
    def x0(self) -> float:
        return self.bbox[0]

    @property
    def y0(self) -> float:
        return self.bbox[1]

    @property
    def x1(self) -> float:
        return self.bbox[2]

    @property
    def y1(self) -> float:
        return self.bbox[3]

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def x_center(self) -> float:
        return (self.x0 + self.x1) / 2.0


class PageText:
    """Extracted text and metadata for a single 1-indexed PDF page."""

    def __init__(
        self,
        page: int,
        blocks: list[TextBlock],
        width: float,
        height: float,
        tables: list[dict] | None = None,
    ):
        self.page = page
        self.blocks = blocks
        self.width = width
        self.height = height
        self.tables = tables or []

    @property
    def clean_text(self) -> str:
        return "\n\n".join(b.text.strip() for b in self.blocks if b.text.strip())


class ParsedPDF:
    """Full parsed representation of a PDF document."""

    def __init__(
        self,
        page_count: int,
        pages: list[PageText],
        references_start_page: int | None = None,
        doc_metadata: dict[str, Any] | None = None,
    ):
        self.page_count = page_count
        self.pages = pages
        self.references_start_page = references_start_page
        self.doc_metadata = doc_metadata or {}

    @property
    def all_blocks(self) -> list[TextBlock]:
        result = []
        for p in self.pages:
            result.extend(p.blocks)
        return result

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.clean_text for p in self.pages if p.clean_text)


def _bbox_overlap(
    bbox1: tuple[float, float, float, float],
    bbox2: tuple[float, float, float, float],
) -> bool:
    """Check if two bounding boxes overlap."""
    x0_1, y0_1, x1_1, y1_1 = bbox1
    x0_2, y0_2, x1_2, y1_2 = bbox2
    return not (x1_1 <= x0_2 or x0_1 >= x1_2 or y1_1 <= y0_2 or y0_1 >= y1_2)


def _table_to_markdown(table) -> str:
    """Convert a PyMuPDF Table object to a clean Markdown string."""
    try:
        data = table.extract()
        if not data or len(data) < 2:
            return ""

        headers = [str(col or "").strip() for col in data[0]]
        header_line = "| " + " | ".join(headers) + " |"
        sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
        row_lines = []
        for row in data[1:]:
            cells = [str(col or "").strip().replace("\n", " ") for col in row]
            row_lines.append("| " + " | ".join(cells) + " |")

        return "\n".join([header_line, sep_line] + row_lines)
    except Exception as e:
        logger.debug("Failed to extract markdown from table: %s", e)
        return ""


def _order_blocks_two_column(
    blocks: list[TextBlock], page_width: float, page_height: float
) -> list[TextBlock]:
    """Order blocks taking into account two-column academic layout.

    03 §2: If page has >= 2 vertical text clusters (x-center gap > 25% page width
    and both columns have >= 5 lines), treat as two-column:
    order = left column top->bottom, then right column.
    Full-width blocks (title, abstract, figures) break columns and stay ordered vertically.
    """
    if not blocks:
        return []

    # Identify full-width blocks: width > 65% of page width, or centered across middle
    left_margin_limit = 0.48 * page_width
    right_margin_limit = 0.52 * page_width

    left_col: list[TextBlock] = []
    right_col: list[TextBlock] = []
    full_width: list[TextBlock] = []

    for b in blocks:
        if b.width > 0.65 * page_width:
            full_width.append(b)
        elif b.x1 <= left_margin_limit or b.x_center < left_margin_limit:
            left_col.append(b)
        elif b.x0 >= right_margin_limit or b.x_center > right_margin_limit:
            right_col.append(b)
        else:
            # Spans the middle or indeterminate
            full_width.append(b)

    # Check if this qualifies as two-column layout:
    # Both columns have >= 2 blocks (or lines), and there is distinct separation
    if len(left_col) >= 2 and len(right_col) >= 2:
        # Segment into vertical bands bounded by full-width blocks
        all_elements = sorted(
            [("full", b.y0, b) for b in full_width]
            + [("left", b.y0, b) for b in left_col]
            + [("right", b.y0, b) for b in right_col],
            key=lambda x: x[1],
        )

        ordered: list[TextBlock] = []
        cur_left: list[TextBlock] = []
        cur_right: list[TextBlock] = []

        for kind, _, b in all_elements:
            if kind == "full":
                # Flush pending two-column blocks: left first, then right
                cur_left.sort(key=lambda x: (x.y0, x.x0))
                cur_right.sort(key=lambda x: (x.y0, x.x0))
                ordered.extend(cur_left)
                ordered.extend(cur_right)
                cur_left = []
                cur_right = []
                ordered.append(b)
            elif kind == "left":
                cur_left.append(b)
            else:
                cur_right.append(b)

        cur_left.sort(key=lambda x: (x.y0, x.x0))
        cur_right.sort(key=lambda x: (x.y0, x.x0))
        ordered.extend(cur_left)
        ordered.extend(cur_right)
        return ordered
    else:
        # Single column layout: sort top-to-bottom, left-to-right
        return sorted(blocks, key=lambda b: (b.y0, b.x0))


def parse_pdf(
    file_path: Path | str,
    min_chars_per_page: int = 200,
    max_pages: int = 80,
) -> ParsedPDF:
    """Parse a PDF document using PyMuPDF.

    Performs:
    - Integrity and size check (CORRUPTED_PDF, EMPTY_PDF, PDF_TOO_LONG)
    - Block & span extraction with font size, bold flags, and bboxes
    - Table extraction (best effort with markdown formatting)
    - Running headers and footers removal (>40% of pages in top/bottom 8% band)
    - Two-column reading order reconstruction
    - Dehyphenation and unicode normalization
    - Scanned PDF detection (SCANNED_PDF_NO_TEXT)
    - Identification of references section start

    Args:
        file_path: Path to the PDF file.
        min_chars_per_page: Minimum chars/page threshold for scanned PDF detection.
        max_pages: Maximum permitted pages.

    Returns:
        ParsedPDF instance with ordered pages, blocks, and tables.

    Raises:
        IngestError: with appropriate error code if document cannot be processed.
    """
    path = Path(file_path)
    if not path.exists():
        raise IngestError(code="CORRUPTED_PDF", message="PDF file not found on disk.")

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        logger.warning("PyMuPDF failed to open %s: %s", path.name, exc)
        raise IngestError(
            code="CORRUPTED_PDF",
            message="Could not open PDF file. The file may be corrupted.",
        )

    try:
        page_count = doc.page_count
        if page_count == 0:
            raise IngestError(
                code="EMPTY_PDF",
                message="PDF contains 0 pages.",
            )

        if page_count > max_pages:
            raise IngestError(
                code="PDF_TOO_LONG",
                message=f"PDF has {page_count} pages, which exceeds the limit of {max_pages} pages.",
                details={"page_count": page_count, "max_pages": max_pages},
            )

        doc_metadata = doc.metadata or {}

        # 1. Collect lines in top/bottom 8% bands to detect running headers/footers
        band_lines_counter: Counter[str] = Counter()
        raw_pages_data: list[dict] = []
        low_char_pages = 0

        for page_idx in range(page_count):
            page = doc[page_idx]
            p_width = page.rect.width
            p_height = page.rect.height
            top_band = 0.08 * p_height
            bot_band = 0.92 * p_height

            # Extract tables best-effort
            tables_data: list[dict] = []
            table_bboxes: list[tuple[float, float, float, float]] = []
            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    for t in tabs.tables:
                        md = _table_to_markdown(t)
                        bbox = tuple(t.bbox)
                        table_bboxes.append(bbox)
                        if md:
                            tables_data.append({"markdown": md, "bbox": bbox, "page": page_idx + 1})
            except Exception as e:
                logger.debug("Table detection skipped on page %d: %s", page_idx + 1, e)

            # Extract dict representation of text
            text_page = page.get_text("dict")
            blocks = text_page.get("blocks", [])

            # Check chars for scanned check
            plain_text = page.get_text("text").strip()
            if len(plain_text) < min_chars_per_page:
                low_char_pages += 1

            # Check band lines for recurring header/footer
            for b in blocks:
                if b.get("type") == 0:  # text block
                    for line in b.get("lines", []):
                        bbox = line.get("bbox", (0, 0, 0, 0))
                        line_text = "".join(s.get("text", "") for s in line.get("spans", [])).strip()
                        if not line_text:
                            continue
                        if bbox[1] <= top_band or bbox[3] >= bot_band:
                            # Normalize line text to detect repeated headers/footers
                            norm = re.sub(r"\d+", "#", line_text).strip()
                            band_lines_counter[norm] += 1

            raw_pages_data.append({
                "page_num": page_idx + 1,
                "width": p_width,
                "height": p_height,
                "blocks": blocks,
                "tables": tables_data,
                "table_bboxes": table_bboxes,
            })

        # Check scanned PDF condition: >= 50% pages have < min_chars_per_page
        if low_char_pages >= (page_count + 1) // 2:
            raise IngestError(
                code="SCANNED_PDF_NO_TEXT",
                message="PDF appears to be scanned or contains insufficient extractable text (no OCR support).",
                details={"page_count": page_count, "low_char_pages": low_char_pages},
            )

        # Lines repeating on > 40% of pages in header/footer band
        header_footer_threshold = max(2, int(0.40 * page_count))
        repeated_band_lines = {
            norm for norm, count in band_lines_counter.items()
            if count >= header_footer_threshold
        }

        # 2. Process each page into clean TextBlocks
        parsed_pages: list[PageText] = []
        references_start_page: int | None = None

        for p_data in raw_pages_data:
            page_num = p_data["page_num"]
            p_width = p_data["width"]
            p_height = p_data["height"]
            top_band = 0.08 * p_height
            bot_band = 0.92 * p_height
            table_bboxes = p_data["table_bboxes"]

            page_blocks: list[TextBlock] = []

            # Add table blocks first
            for t in p_data["tables"]:
                page_blocks.append(
                    TextBlock(
                        text=t["markdown"],
                        bbox=t["bbox"],
                        font_size=9.0,
                        is_bold=False,
                        page=page_num,
                        is_table=True,
                    )
                )

            for b in p_data["blocks"]:
                if b.get("type") != 0:
                    continue  # Skip image blocks

                b_bbox = tuple(b.get("bbox", (0, 0, 0, 0)))

                # If block overlaps with an extracted table, skip it to avoid duplicate content
                if any(_bbox_overlap(b_bbox, tb) for tb in table_bboxes):
                    continue

                # Process lines and spans in this block
                block_lines: list[str] = []
                span_sizes: list[float] = []
                span_bolds: list[bool] = []

                for line in b.get("lines", []):
                    line_bbox = line.get("bbox", (0, 0, 0, 0))
                    line_text = "".join(s.get("text", "") for s in line.get("spans", []))

                    # Drop running header / footer lines
                    norm_line = re.sub(r"\d+", "#", line_text).strip()
                    if (line_bbox[1] <= top_band or line_bbox[3] >= bot_band) and norm_line in repeated_band_lines:
                        continue

                    # Collect typography
                    for s in line.get("spans", []):
                        span_text = s.get("text", "")
                        if span_text.strip():
                            span_sizes.extend([s.get("size", 10.0)] * len(span_text))
                            # Flags: bit 4 is bold
                            flags = s.get("flags", 0)
                            is_bold = bool(flags & 2 ** 4) or "bold" in s.get("font", "").lower()
                            span_bolds.append(is_bold)

                    if line_text.strip():
                        block_lines.append(line_text)

                if not block_lines:
                    continue

                raw_block_text = "\n".join(block_lines)

                # Clean text: dehyphenate, normalize NFKC
                cleaned_text = dehyphenate(raw_block_text)
                cleaned_text = unicodedata.normalize("NFKC", cleaned_text).strip()

                if not cleaned_text:
                    continue

                avg_font_size = (
                    sum(span_sizes) / len(span_sizes) if span_sizes else 10.0
                )
                is_bold_block = (
                    (sum(span_bolds) / len(span_bolds) >= 0.5) if span_bolds else False
                )
                is_caption = bool(CAPTION_RE.match(cleaned_text))

                # Check if this block introduces the References heading
                if references_start_page is None and REF_HEADING_RE.match(cleaned_text):
                    references_start_page = page_num

                page_blocks.append(
                    TextBlock(
                        text=cleaned_text,
                        bbox=b_bbox,
                        font_size=avg_font_size,
                        is_bold=is_bold_block,
                        page=page_num,
                        is_table=False,
                        is_caption=is_caption,
                    )
                )

            # Order blocks with two-column awareness
            ordered_blocks = _order_blocks_two_column(page_blocks, p_width, p_height)
            parsed_pages.append(
                PageText(
                    page=page_num,
                    blocks=ordered_blocks,
                    width=p_width,
                    height=p_height,
                    tables=p_data["tables"],
                )
            )

        return ParsedPDF(
            page_count=page_count,
            pages=parsed_pages,
            references_start_page=references_start_page,
            doc_metadata=doc_metadata,
        )

    finally:
        doc.close()
