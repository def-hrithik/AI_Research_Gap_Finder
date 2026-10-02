"""
Projects API — 06 §13.
POST/GET /api/projects, GET/DELETE /api/projects/{id}.
Routes are thin: validate → call service → map to schema (08 §2).
"""

from fastapi import APIRouter, Query

from app.api.deps import DbDep, SettingsDep
from app.core.errors import ProjectNotFoundError
from app.core.ids import new_id
from app.database import repos
from app.schemas.common import ListEnvelope
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


def _project_to_response(project, db) -> ProjectResponse:
    """Map a Project ORM object to a ProjectResponse with derived fields."""
    counts = repos.count_papers_by_status(db, project.project_id)
    total = sum(counts.values())
    indexed = counts.get("INDEXED", 0) + counts.get("ANALYZED", 0) + counts.get("ANALYZING", 0)
    analyzed = counts.get("ANALYZED", 0)

    # Derive project status — 06 §13
    if total == 0:
        status = "EMPTY"
    elif any(s in counts for s in ["UPLOADED", "PARSING", "CHUNKING", "EMBEDDING", "ANALYZING"]):
        status = "PROCESSING"
    elif counts.get("FAILED", 0) == total:
        status = "ERROR"
    elif analyzed > 0:
        status = "ANALYZED"
    else:
        status = "PROCESSING"

    # Gap and topic counts from latest run
    gap_count = 0
    topic_count = 0
    latest_run = repos.get_latest_run(db, project.project_id)
    if latest_run and latest_run.result:
        gap_count = len(latest_run.result.get("research_gaps", []))
        topic_count = len(latest_run.result.get("themes", []))

    return ProjectResponse(
        project_id=project.project_id,
        name=project.name,
        description=project.description or "",
        paper_count=total,
        indexed_paper_count=indexed,
        analyzed_paper_count=analyzed,
        status=status,
        gap_count=gap_count,
        topic_count=topic_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("", status_code=201, response_model=ProjectResponse)
async def create_project(body: ProjectCreate, db: DbDep) -> ProjectResponse:
    """Create a new project — 06 §13."""
    project_id = new_id("prj")
    project = repos.create_project(db, project_id, body.name, body.description)
    return _project_to_response(project, db)


@router.get("", response_model=ListEnvelope[ProjectResponse])
async def list_projects(
    db: DbDep,
    q: str | None = None,
    sort: str = Query(default="updated_at", pattern="^(updated_at|name|created_at)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ListEnvelope[ProjectResponse]:
    """List projects — 06 §13."""
    items, total = repos.list_projects(db, q=q, sort=sort, order=order, limit=limit, offset=offset)
    return ListEnvelope(
        items=[_project_to_response(p, db) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: DbDep) -> ProjectResponse:
    """Get a single project — 06 §13."""
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)
    return _project_to_response(project, db)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, db: DbDep) -> None:
    """Delete a project and cascade all data — 06 §13."""
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)
    # TODO: Also delete Qdrant points and uploaded files when those modules exist
    repos.delete_project(db, project_id)
