"""
Chunk and section schemas — 05 §5.3, 03 §3–4.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict


class ChunkResponse(BaseModel):
    """Chunk schema — 05 §5.3."""
    model_config = ConfigDict(from_attributes=True)

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


class Paragraph(BaseModel):
    """Paragraph extracted from a document page."""
    text: str
    page: int
    is_table: bool = False


class Section(BaseModel):
    """Detected document section — 03 §3."""
    heading: str
    chunk_type: str
    page_start: int
    page_end: int
    paragraphs: list[Paragraph] = []
    has_future_cue: bool = False
    has_limitation_cue: bool = False
