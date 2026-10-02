"""
Repository layer — 08 §2.
Thin data-access functions over SQLAlchemy. No business logic.
"""

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import (
    Chunk,
    Contradiction,
    Evidence,
    FutureDirection,
    Job,
    Paper,
    PaperAnalysis,
    Project,
    ResearchGap,
    ResearchReport,
    ResearchRun,
)


# ============================================================
# Projects
# ============================================================

def create_project(db: Session, project_id: str, name: str, description: str = "") -> Project:
    project = Project(project_id=project_id, name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: str) -> Project | None:
    return db.query(Project).filter(Project.project_id == project_id).first()


def list_projects(
    db: Session, q: str | None = None, sort: str = "updated_at",
    order: str = "desc", limit: int = 50, offset: int = 0,
) -> tuple[list[Project], int]:
    query = db.query(Project)
    if q:
        query = query.filter(Project.name.ilike(f"%{q}%"))

    total = query.count()

    sort_col = getattr(Project, sort, Project.updated_at)
    if order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    items = query.offset(offset).limit(limit).all()
    return items, total


def delete_project(db: Session, project_id: str) -> None:
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project:
        db.delete(project)
        db.commit()


def count_papers_by_status(db: Session, project_id: str) -> dict[str, int]:
    """Count papers grouped by status for a project."""
    rows = (
        db.query(Paper.status, func.count(Paper.paper_id))
        .filter(Paper.project_id == project_id)
        .group_by(Paper.status)
        .all()
    )
    return {status: count for status, count in rows}


def count_papers_in_project(db: Session, project_id: str) -> int:
    """Count total papers in a project."""
    return db.query(Paper).filter(Paper.project_id == project_id).count()


# ============================================================
# Papers
# ============================================================

def create_paper(db: Session, **kwargs) -> Paper:
    paper = Paper(**kwargs)
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper


def get_paper(db: Session, paper_id: str) -> Paper | None:
    return db.query(Paper).filter(Paper.paper_id == paper_id).first()


def get_paper_by_sha256(db: Session, project_id: str, sha256: str) -> Paper | None:
    return (
        db.query(Paper)
        .filter(Paper.project_id == project_id, Paper.sha256 == sha256)
        .first()
    )


def list_papers(
    db: Session, project_id: str, status: list[str] | None = None,
    q: str | None = None, sort: str = "created_at", order: str = "desc",
    limit: int = 50, offset: int = 0,
) -> tuple[list[Paper], int]:
    query = db.query(Paper).filter(Paper.project_id == project_id)

    if status:
        query = query.filter(Paper.status.in_(status))
    if q:
        query = query.filter(
            Paper.title.ilike(f"%{q}%") | Paper.authors.cast(str).ilike(f"%{q}%")
        )

    total = query.count()

    sort_col = getattr(Paper, sort, Paper.created_at)
    if order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    items = query.offset(offset).limit(limit).all()
    return items, total


def update_paper_status(
    db: Session, paper_id: str, status: str,
    error_code: str | None = None, error_message: str | None = None,
    **kwargs,
) -> None:
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if paper:
        paper.status = status
        paper.error_code = error_code
        paper.error_message = error_message
        for k, v in kwargs.items():
            if hasattr(paper, k):
                setattr(paper, k, v)
        paper.updated_at = datetime.now(timezone.utc)
        db.commit()


def delete_paper(db: Session, paper_id: str) -> None:
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if paper:
        db.delete(paper)
        db.commit()


# ============================================================
# Chunks
# ============================================================

def bulk_create_chunks(db: Session, chunks: list[dict]) -> None:
    db.bulk_insert_mappings(Chunk, chunks)
    db.commit()


# Alias used by ingest_service
create_chunks_batch = bulk_create_chunks


def get_chunks_by_paper(
    db: Session, paper_id: str, chunk_type: str | None = None,
    limit: int = 500, offset: int = 0,
) -> list[Chunk]:
    query = db.query(Chunk).filter(Chunk.paper_id == paper_id)
    if chunk_type:
        query = query.filter(Chunk.chunk_type == chunk_type)
    return query.order_by(Chunk.chunk_index).offset(offset).limit(limit).all()


# Alias used by services
list_chunks_by_paper = get_chunks_by_paper


def get_chunks_by_project(db: Session, project_id: str, exclude_references: bool = True) -> list[Chunk]:
    """Get all chunks for a project, optionally excluding REFERENCES (for BM25)."""
    query = db.query(Chunk).filter(Chunk.project_id == project_id)
    if exclude_references:
        query = query.filter(Chunk.chunk_type != "REFERENCES")
    return query.order_by(Chunk.paper_id, Chunk.chunk_index).all()


# Alias used by services
list_chunks_by_project = get_chunks_by_project


def get_chunk(db: Session, chunk_id: str) -> Chunk | None:
    return db.query(Chunk).filter(Chunk.chunk_id == chunk_id).first()


def delete_chunks_by_paper(db: Session, paper_id: str) -> None:
    db.query(Chunk).filter(Chunk.paper_id == paper_id).delete()
    db.commit()


# ============================================================
# Jobs
# ============================================================

def create_job(db: Session, **kwargs) -> Job:
    job = Job(**kwargs)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> Job | None:
    return db.query(Job).filter(Job.job_id == job_id).first()


def update_job(db: Session, job_id: str, **kwargs) -> None:
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job:
        for k, v in kwargs.items():
            if hasattr(job, k):
                setattr(job, k, v)
        db.commit()


def mark_interrupted_jobs(db: Session) -> int:
    """On startup, mark RUNNING jobs as FAILED(INTERRUPTED) — 02 §7."""
    count = (
        db.query(Job)
        .filter(Job.status.in_(["QUEUED", "RUNNING"]))
        .update(
            {
                "status": "FAILED",
                "error_code": "INTERRUPTED",
                "error_message": "Server restarted while job was running.",
                "finished_at": datetime.now(timezone.utc),
            },
            synchronize_session="fetch",
        )
    )
    db.commit()
    return count


# ============================================================
# Paper Analysis
# ============================================================

def get_analysis_by_cache_key(
    db: Session, paper_id: str, prompt_version: str, llm_model: str,
) -> PaperAnalysis | None:
    return (
        db.query(PaperAnalysis)
        .filter(
            PaperAnalysis.paper_id == paper_id,
            PaperAnalysis.prompt_version == prompt_version,
            PaperAnalysis.llm_model == llm_model,
        )
        .first()
    )


def get_latest_analysis(db: Session, paper_id: str) -> PaperAnalysis | None:
    return (
        db.query(PaperAnalysis)
        .filter(PaperAnalysis.paper_id == paper_id)
        .order_by(PaperAnalysis.created_at.desc())
        .first()
    )


def create_analysis(db: Session, **kwargs) -> PaperAnalysis:
    analysis = PaperAnalysis(**kwargs)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


# ============================================================
# Research Runs
# ============================================================

def create_run(db: Session, **kwargs) -> ResearchRun:
    run = ResearchRun(**kwargs)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_run(db: Session, run_id: str) -> ResearchRun | None:
    return db.query(ResearchRun).filter(ResearchRun.run_id == run_id).first()


def get_latest_run(db: Session, project_id: str, status: str = "SUCCEEDED") -> ResearchRun | None:
    return (
        db.query(ResearchRun)
        .filter(ResearchRun.project_id == project_id, ResearchRun.status == status)
        .order_by(ResearchRun.created_at.desc())
        .first()
    )


# ============================================================
# Gaps
# ============================================================

def list_gaps(
    db: Session, project_id: str, run_id: str | None = None,
    category: str | None = None, gap_type: str | None = None,
    min_confidence: float | None = None, sort: str = "confidence",
    order: str = "desc", limit: int = 50, offset: int = 0,
) -> tuple[list[ResearchGap], int]:
    query = db.query(ResearchGap).filter(ResearchGap.project_id == project_id)
    if run_id:
        query = query.filter(ResearchGap.run_id == run_id)
    if category:
        query = query.filter(ResearchGap.category == category)
    if gap_type:
        query = query.filter(ResearchGap.gap_type == gap_type)
    if min_confidence is not None:
        query = query.filter(ResearchGap.confidence >= min_confidence)

    total = query.count()

    sort_col = getattr(ResearchGap, sort, ResearchGap.confidence)
    if order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    items = query.offset(offset).limit(limit).all()
    return items, total


def get_gap(db: Session, gap_id: str) -> ResearchGap | None:
    return db.query(ResearchGap).filter(ResearchGap.gap_id == gap_id).first()


def create_gap(db: Session, **kwargs) -> ResearchGap:
    gap = ResearchGap(**kwargs)
    db.add(gap)
    db.commit()
    db.refresh(gap)
    return gap


# ============================================================
# Contradictions
# ============================================================

def create_contradiction(db: Session, **kwargs) -> Contradiction:
    c = Contradiction(**kwargs)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def list_contradictions(db: Session, project_id: str, run_id: str | None = None) -> list[Contradiction]:
    query = db.query(Contradiction).filter(Contradiction.project_id == project_id)
    if run_id:
        query = query.filter(Contradiction.run_id == run_id)
    return query.order_by(Contradiction.created_at.desc()).all()


# ============================================================
# Reports
# ============================================================

def create_report(db: Session, **kwargs) -> ResearchReport:
    report = ResearchReport(**kwargs)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report(db: Session, report_id: str) -> ResearchReport | None:
    return db.query(ResearchReport).filter(ResearchReport.report_id == report_id).first()


def get_latest_report(db: Session, project_id: str) -> ResearchReport | None:
    return (
        db.query(ResearchReport)
        .filter(ResearchReport.project_id == project_id)
        .order_by(ResearchReport.created_at.desc())
        .first()
    )


def list_reports(db: Session, project_id: str) -> list[ResearchReport]:
    return (
        db.query(ResearchReport)
        .filter(ResearchReport.project_id == project_id)
        .order_by(ResearchReport.created_at.desc())
        .all()
    )




