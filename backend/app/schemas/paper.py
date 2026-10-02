"""
Paper schemas — 05 §5.2, 06 §3–5.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class PaperSourceInfo(BaseModel):
    """Paper source file info — 05 §5.2."""
    model_config = ConfigDict(from_attributes=True)

    filename: str
    sha256: str | None = None
    size_bytes: int | None = None
    page_count: int | None = None


class PaperErrorInfo(BaseModel):
    """Paper error details — 05 §5.16."""
    code: str
    message: str


class PaperResponse(BaseModel):
    """Paper response — 05 §5.2."""
    model_config = ConfigDict(from_attributes=True)

    paper_id: str
    project_id: str
    title: str
    authors: list[str] = []
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    abstract: str | None = None
    domain: str | None = None
    status: str
    error: PaperErrorInfo | None = None
    source: PaperSourceInfo
    metadata_confidence: float | None = None
    section_detection_quality: str | None = None
    has_analysis: bool = False
    analysis_status: str = "NONE"
    warnings: list[str] = []
    created_at: datetime
    updated_at: datetime | None = None


class PaperUploadResponse(BaseModel):
    """Response for POST /api/projects/{id}/papers/upload — 06 §3."""
    paper: PaperResponse
    job_id: str
    poll_url: str


class PaperDetailResponse(BaseModel):
    """Response for GET /api/papers/{id} — 06 §5."""
    paper: PaperResponse
    analysis: dict[str, Any] | None = None
    analysis_status: str = "NONE"


def to_paper_response(paper: Any, has_analysis: bool = False, analysis_status: str = "NONE") -> PaperResponse:
    """Map SQLAlchemy Paper model to PaperResponse schema."""
    error = None
    if paper.error_code:
        error = PaperErrorInfo(code=paper.error_code, message=paper.error_message or "")

    source = PaperSourceInfo(
        filename=paper.source_filename,
        sha256=paper.sha256,
        size_bytes=paper.size_bytes,
        page_count=paper.page_count,
    )

    authors_list = paper.authors if isinstance(paper.authors, list) else []

    return PaperResponse(
        paper_id=paper.paper_id,
        project_id=paper.project_id,
        title=paper.title,
        authors=authors_list,
        year=paper.year,
        venue=paper.venue,
        doi=paper.doi,
        abstract=paper.abstract,
        domain=paper.domain,
        status=paper.status,
        error=error,
        source=source,
        metadata_confidence=paper.metadata_confidence,
        section_detection_quality=paper.section_detection_quality,
        has_analysis=has_analysis,
        analysis_status=analysis_status,
        warnings=[],
        created_at=paper.created_at,
        updated_at=paper.updated_at,
    )
