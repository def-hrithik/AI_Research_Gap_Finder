"""
Job service — 02 §7, 08 §11.
Job runner with bounded thread pool for CPU-bound tasks.
Stage/progress updates and startup sweep.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Callable

from app.core.logging import ctx_job_id, ctx_project_id, ctx_paper_id
from app.database import repos
from app.database.session import get_session

logger = logging.getLogger("rgf.services.job")

# Module-level thread pool, initialized by init_job_runner()
_executor: ThreadPoolExecutor | None = None


def init_job_runner(max_concurrency: int = 2) -> None:
    """Initialize the background job thread pool — 02 §7.

    Args:
        max_concurrency: Max concurrent CPU-bound jobs (ANALYSIS_MAX_CONCURRENCY).
    """
    global _executor
    _executor = ThreadPoolExecutor(
        max_workers=max_concurrency,
        thread_name_prefix="rgf-job",
    )
    logger.info("Job runner initialized with %d workers", max_concurrency)


def submit_job(job_id: str, func: Callable, *args, **kwargs) -> None:
    """Submit a function to run as a background job.

    The function receives the job_id as its first argument.
    It should call update_job_stage() to report progress.

    Args:
        job_id: The job ID to track.
        func: Callable to execute in the thread pool.
        *args: Additional positional args for func.
        **kwargs: Additional keyword args for func.
    """
    if _executor is None:
        raise RuntimeError("Job runner not initialized. Call init_job_runner() first.")

    def wrapper():
        # Set context vars for structured logging
        ctx_job_id.set(job_id)

        db = get_session()
        try:
            # Mark job as running
            repos.update_job(
                db, job_id,
                status="RUNNING",
                started_at=datetime.now(timezone.utc),
            )
            logger.info("Job %s started", job_id, extra={"event": "job.running"})

            # Execute the job function
            result = func(job_id, db, *args, **kwargs)

            # Mark job as succeeded
            repos.update_job(
                db, job_id,
                status="SUCCEEDED",
                progress=1.0,
                result=result,
                finished_at=datetime.now(timezone.utc),
            )
            logger.info("Job %s succeeded", job_id, extra={"event": "job.succeeded"})

        except Exception as exc:
            logger.exception(
                "Job %s failed: %s", job_id, str(exc),
                extra={"event": "job.failed"},
            )
            error_code = getattr(exc, "code", "INTERNAL_ERROR")
            error_message = getattr(exc, "message", str(exc))
            repos.update_job(
                db, job_id,
                status="FAILED",
                error_code=error_code,
                error_message=error_message,
                finished_at=datetime.now(timezone.utc),
            )
        finally:
            db.close()
            ctx_job_id.set(None)

    _executor.submit(wrapper)


def update_job_stage(db, job_id: str, stage: str, progress: float) -> None:
    """Update a running job's stage and progress.

    Called by job functions between pipeline stages (08 §11).

    Args:
        db: SQLAlchemy session (the job's own session).
        job_id: The job to update.
        stage: Current pipeline stage name.
        progress: Progress fraction (0.0-1.0).
    """
    repos.update_job(db, job_id, stage=stage, progress=min(progress, 1.0))
    logger.info(
        "Job %s stage=%s progress=%.0f%%",
        job_id, stage, progress * 100,
        extra={"event": "job.stage", "stage": stage, "progress": progress},
    )


def startup_sweep() -> int:
    """Mark any RUNNING/QUEUED jobs as FAILED(INTERRUPTED) on startup — 02 §7.

    Returns:
        Number of jobs marked as interrupted.
    """
    db = get_session()
    try:
        count = repos.mark_interrupted_jobs(db)
        if count > 0:
            logger.warning(
                "Marked %d interrupted jobs as FAILED on startup", count,
                extra={"event": "job.startup_sweep", "count": count},
            )
        return count
    finally:
        db.close()


def shutdown_job_runner() -> None:
    """Shut down the thread pool gracefully."""
    global _executor
    if _executor:
        _executor.shutdown(wait=False)
        _executor = None
        logger.info("Job runner shut down")
