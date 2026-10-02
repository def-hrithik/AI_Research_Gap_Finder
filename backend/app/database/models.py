"""
SQLAlchemy models — 05 §4.
All relational tables for the backend. Postgres-compatible via SQLAlchemy.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    """Projects table — 05 §4."""
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")
    research_runs = relationship("ResearchRun", back_populates="project", cascade="all, delete-orphan")


class Paper(Base):
    """Papers table — 05 §4."""
    __tablename__ = "papers"
    __table_args__ = (
        UniqueConstraint("project_id", "sha256", name="uq_paper_project_sha256"),
        Index("ix_paper_project", "project_id"),
    )

    paper_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    authors = Column(JSON, default=list)  # list[str]
    year = Column(Integer, nullable=True)
    venue = Column(String, nullable=True)
    doi = Column(String, nullable=True, index=True)
    abstract = Column(Text, nullable=True)
    source_filename = Column(String, nullable=False)
    sha256 = Column(String(64), nullable=True, index=True)
    size_bytes = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="UPLOADED")
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_confidence = Column(Float, nullable=True)
    section_detection_quality = Column(String(10), nullable=True)
    domain = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    project = relationship("Project", back_populates="papers")
    chunks = relationship("Chunk", back_populates="paper", cascade="all, delete-orphan")
    analyses = relationship("PaperAnalysis", back_populates="paper", cascade="all, delete-orphan")


class Chunk(Base):
    """Chunks table — 05 §4."""
    __tablename__ = "chunks"
    __table_args__ = (
        Index("ix_chunk_paper", "paper_id"),
        Index("ix_chunk_project", "project_id"),
    )

    chunk_id = Column(String, primary_key=True)
    paper_id = Column(String, ForeignKey("papers.paper_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    section_heading = Column(String, nullable=True)
    chunk_type = Column(String(20), nullable=False)
    page = Column(Integer, nullable=False)
    page_end = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    is_table = Column(Boolean, default=False)
    has_future_cue = Column(Boolean, default=False)
    has_limitation_cue = Column(Boolean, default=False)
    embedding_model = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    paper = relationship("Paper", back_populates="chunks")


class PaperAnalysis(Base):
    """Paper analyses table — 05 §4."""
    __tablename__ = "paper_analyses"
    __table_args__ = (
        UniqueConstraint("paper_id", "prompt_version", "llm_model", name="uq_analysis_cache"),
        Index("ix_analysis_paper", "paper_id"),
    )

    analysis_id = Column(String, primary_key=True)
    paper_id = Column(String, ForeignKey("papers.paper_id", ondelete="CASCADE"), nullable=False)
    prompt_version = Column(String, nullable=False)
    llm_model = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)  # PaperAnalysis JSON
    status = Column(String(20), nullable=False, default="RUNNING")
    llm_calls = Column(Integer, default=0)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    paper = relationship("Paper", back_populates="analyses")


class Evidence(Base):
    """Evidence table — 05 §4."""
    __tablename__ = "evidence"
    __table_args__ = (
        Index("ix_evidence_owner", "owner_id"),
    )

    evidence_id = Column(String, primary_key=True)
    owner_type = Column(String(20), nullable=False)  # OwnerType enum
    owner_id = Column(String, nullable=False, index=True)
    paper_id = Column(String, nullable=True)
    chunk_id = Column(String, nullable=True)
    page = Column(Integer, nullable=True)
    section = Column(String(20), nullable=True)
    chunk_type = Column(String(20), nullable=True)
    quote = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    verified = Column(Boolean, default=False)
    quote_fuzzy = Column(Boolean, default=False)
    entailment = Column(String(20), default="NOT_CHECKED")
    role = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ResearchRun(Base):
    """Research runs table — 05 §4."""
    __tablename__ = "research_runs"
    __table_args__ = (
        Index("ix_run_project", "project_id"),
    )

    run_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=True)
    paper_ids = Column(JSON, default=list)
    analysis_depth = Column(String(10), default="standard")
    target = Column(String(20), default="FULL")  # RunTarget
    status = Column(String(20), nullable=False, default="RUNNING")
    result = Column(JSON, nullable=True)  # Full ResearchAnalysisResult
    paper_set_hash = Column(String(64), nullable=True)
    prompt_versions = Column(JSON, default=dict)
    stats = Column(JSON, default=dict)
    warnings = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="research_runs")
    gaps = relationship("ResearchGap", back_populates="run", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="run", cascade="all, delete-orphan")
    future_directions = relationship("FutureDirection", back_populates="run", cascade="all, delete-orphan")
    reports = relationship("ResearchReport", back_populates="run", cascade="all, delete-orphan")


class ResearchGap(Base):
    """Research gaps table — 05 §4."""
    __tablename__ = "research_gaps"
    __table_args__ = (
        Index("ix_gap_run", "run_id"),
        Index("ix_gap_project", "project_id"),
    )

    gap_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("research_runs.run_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, nullable=False, index=True)
    payload = Column(JSON, nullable=False)  # Full ResearchGap JSON
    category = Column(String(20), nullable=False)
    gap_type = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    evidence_strength = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    run = relationship("ResearchRun", back_populates="gaps")


class Contradiction(Base):
    """Contradictions table — 05 §4."""
    __tablename__ = "contradictions"

    contradiction_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("research_runs.run_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    run = relationship("ResearchRun", back_populates="contradictions")


class FutureDirection(Base):
    """Future directions table — 05 §4."""
    __tablename__ = "future_directions"

    direction_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("research_runs.run_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    frequency = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    run = relationship("ResearchRun", back_populates="future_directions")


class ResearchReport(Base):
    """Research reports table — 05 §4."""
    __tablename__ = "research_reports"

    report_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("research_runs.run_id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    payload = Column(JSON, nullable=False)
    markdown = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    run = relationship("ResearchRun", back_populates="reports")


class Job(Base):
    """Jobs table — 05 §4."""
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)
    job_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="QUEUED")
    stage = Column(String(40), nullable=True)
    progress = Column(Float, default=0.0)
    project_id = Column(String, nullable=True)
    paper_id = Column(String, nullable=True)
    run_id = Column(String, nullable=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
