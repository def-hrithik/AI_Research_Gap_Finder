"""
Project schemas — 05 §5.1, 06 §13.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Request body for POST /api/projects — 06 §13."""
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)


class ProjectSource(BaseModel):
    """Paper source metadata subset for project context."""
    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """Project response — 05 §5.1 + 06 §14.1 derived fields."""
    model_config = ConfigDict(from_attributes=True)

    project_id: str
    name: str
    description: str
    paper_count: int = 0
    indexed_paper_count: int = 0
    analyzed_paper_count: int = 0
    status: str = "EMPTY"
    gap_count: int = 0
    topic_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None
