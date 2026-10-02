"""
Research Analysis API routes — 06 §8–9, §13.
Endpoints for:
- Research Gaps: GET /projects/{id}/gaps, GET /gaps/{id}
- Contradictions: GET /projects/{id}/contradictions
- Landscape: GET /projects/{id}/landscape
- Reports: GET/POST /projects/{id}/reports, GET /reports/{id}
- Trigger Analysis: POST /projects/{id}/analyze
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import ProjectNotFoundError
from app.database import repos
from app.services.research_service import execute_project_research_analysis

router = APIRouter(tags=["research"])


@router.post("/projects/{project_id}/analyze", summary="Run research synthesis on project papers")
async def trigger_project_analysis(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    return await execute_project_research_analysis(project_id, db)


@router.get("/projects/{project_id}/gaps", summary="List research gaps for project")
async def list_project_gaps(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    gaps_db, total = repos.list_gaps(db, project_id=project_id)

    # If no gaps yet but papers exist, run analysis dynamically
    if total == 0:
        paper_count = repos.count_papers_in_project(db, project_id)
        if paper_count > 0:
            analysis_res = await execute_project_research_analysis(project_id, db)
            return analysis_res.get("gaps", [])

    return [g.payload for g in gaps_db]


@router.get("/gaps/{gap_id}", summary="Get single research gap by ID")
async def get_gap_by_id(
    gap_id: str,
    db: Session = Depends(get_db),
):
    gap = repos.get_gap(db, gap_id)
    if not gap:
        raise HTTPException(status_code=404, detail=f"Gap {gap_id} not found")
    return gap.payload


@router.get("/projects/{project_id}/contradictions", summary="List contradictions for project")
async def list_project_contradictions(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    items = repos.list_contradictions(db, project_id=project_id)
    if not items:
        paper_count = repos.count_papers_in_project(db, project_id)
        if paper_count >= 2:
            analysis_res = await execute_project_research_analysis(project_id, db)
            return analysis_res.get("contradictions", [])

    return [c.payload for c in items]


@router.get("/projects/{project_id}/landscape", summary="Get research landscape synthesis")
async def get_project_landscape(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    run = repos.get_latest_run(db, project_id=project_id)
    if run and run.result and "landscape" in run.result:
        return run.result["landscape"]

    paper_count = repos.count_papers_in_project(db, project_id)
    if paper_count > 0:
        res = await execute_project_research_analysis(project_id, db)
        return res.get("landscape", {})

    return {
        "topicClusters": [],
        "methodologies": [],
        "repeatedLimitations": [],
        "datasets": [],
    }


@router.get("/projects/{project_id}/reports", summary="Get latest research report for project")
async def get_project_reports(
    project_id: str,
    format: str | None = Query(None),
    db: Session = Depends(get_db),
):
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    report = repos.get_latest_report(db, project_id=project_id)
    if not report:
        paper_count = repos.count_papers_in_project(db, project_id)
        if paper_count > 0:
            res = await execute_project_research_analysis(project_id, db)
            report = repos.get_report(db, res["report_id"])

    if not report:
        raise HTTPException(status_code=404, detail="No report generated yet.")

    if format == "md":
        return Response(
            content=report.markdown or "",
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="research-report-{project_id}.md"'},
        )

    return {
        "report_id": report.report_id,
        "project_id": report.project_id,
        "title": report.title,
        "markdown": report.markdown,
        "payload": report.payload,
        "created_at": report.created_at,
    }


@router.post("/projects/{project_id}/reports/generate", summary="Generate fresh report")
async def generate_project_report(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    res = await execute_project_research_analysis(project_id, db)
    report = repos.get_report(db, res["report_id"])
    return {
        "report_id": report.report_id if report else res["report_id"],
        "project_id": project_id,
        "title": report.title if report else f"Research Report — {project.name}",
        "markdown": report.markdown if report else res.get("markdown", ""),
    }


@router.get("/reports/{report_id}", summary="Get report by ID")
async def get_report_by_id(
    report_id: str,
    format: str | None = Query(None),
    db: Session = Depends(get_db),
):
    report = repos.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    if format == "md":
        return Response(
            content=report.markdown or "",
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="report-{report_id}.md"'},
        )

    return {
        "report_id": report.report_id,
        "project_id": report.project_id,
        "title": report.title,
        "markdown": report.markdown,
        "payload": report.payload,
        "created_at": report.created_at,
    }
