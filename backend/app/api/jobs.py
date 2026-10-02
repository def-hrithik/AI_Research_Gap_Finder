"""
Jobs API — 06 §10.
GET /api/jobs/{job_id} — poll job status.
"""

from fastapi import APIRouter, Response

from app.api.deps import DbDep
from app.core.errors import JobNotFoundError
from app.database import repos
from app.schemas.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: DbDep, response: Response) -> JobResponse:
    """Poll a job's status — 06 §10.

    Returns Retry-After header while QUEUED or RUNNING.
    """
    job = repos.get_job(db, job_id)
    if not job:
        raise JobNotFoundError(job_id)

    # Add Retry-After for in-progress jobs — 06 §1.5
    if job.status in ("QUEUED", "RUNNING"):
        response.headers["Retry-After"] = "2"

    error_dict = None
    if job.error_code:
        error_dict = {
            "code": job.error_code,
            "message": job.error_message or "",
        }

    return JobResponse(
        job_id=job.job_id,
        job_type=job.job_type,
        status=job.status,
        stage=job.stage,
        progress=job.progress or 0.0,
        project_id=job.project_id,
        paper_id=job.paper_id,
        run_id=job.run_id,
        error=error_dict,
        result=job.result,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )
