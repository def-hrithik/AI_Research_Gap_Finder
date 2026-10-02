"""
Job schemas — 05 §5.15, 06 §1.5.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    """Job status response — 05 §5.15."""
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    job_type: str
    status: str
    stage: str | None = None
    progress: float = 0.0
    project_id: str | None = None
    paper_id: str | None = None
    run_id: str | None = None
    error: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class JobAccepted(BaseModel):
    """Response for 202 Accepted — 06 §1.5."""
    job_id: str
    job_type: str
    status: str = "QUEUED"
    run_id: str | None = None
    poll_url: str
    deduplicated: bool = False
