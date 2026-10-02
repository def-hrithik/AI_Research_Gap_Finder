"""
Paper and Upload API endpoints — 06 §3, §4, §5, §13.
"""

from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import PaperNotFoundError, ProjectNotFoundError
from app.core.files import (
    delete_paper_file,
    get_paper_file_path,
    save_uploaded_pdf,
)
from app.core.ids import new_id
from app.database import repos
from app.database.qdrant import get_vector_store
from app.schemas.chunk import ChunkResponse
from app.schemas.common import ListEnvelope
from app.schemas.paper import (
    PaperDetailResponse,
    PaperResponse,
    PaperUploadResponse,
    to_paper_response,
)
from app.services.ingest_service import start_paper_ingestion

router = APIRouter(tags=["papers"])


@router.post(
    "/projects/{project_id}/papers/upload",
    response_model=PaperUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload PDF paper (canonical)",
)
async def upload_paper_canonical(
    project_id: str,
    response: Response,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload one PDF and start the async ingestion job (06 §3)."""
    # Verify project exists
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    paper_id = new_id("pap")
    original_filename = file.filename or "uploaded.pdf"

    # Stream, validate (magic bytes, size, duplicate sha256), and save to disk
    file_path, sha256_hex, total_bytes = await save_uploaded_pdf(
        upload_file=file,
        paper_id=paper_id,
        project_id=project_id,
    )

    # Initial title is filename stem
    initial_title = Path(original_filename).stem.replace("_", " ").replace("-", " ")

    # Create Paper record with status=PARSING
    paper = repos.create_paper(
        db=db,
        paper_id=paper_id,
        project_id=project_id,
        title=initial_title,
        source_filename=original_filename,
        sha256=sha256_hex,
        size_bytes=total_bytes,
        status="PARSING",
    )

    # Queue background ingestion job
    job_id = start_paper_ingestion(
        project_id=project_id,
        paper_id=paper_id,
        file_path=file_path,
        filename=original_filename,
        db=db,
    )

    poll_url = f"/api/jobs/{job_id}"
    response.headers["Location"] = poll_url

    return PaperUploadResponse(
        paper=to_paper_response(paper),
        job_id=job_id,
        poll_url=poll_url,
    )


@router.post(
    "/papers/upload",
    response_model=PaperUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload PDF paper (alias)",
)
async def upload_paper_alias(
    response: Response,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Alias for paper upload passing project_id as form field (06 §3)."""
    return await upload_paper_canonical(
        project_id=project_id,
        response=response,
        file=file,
        db=db,
    )


@router.get(
    "/projects/{project_id}/papers",
    response_model=ListEnvelope[PaperResponse],
    summary="List project papers",
)
def list_project_papers(
    project_id: str,
    status: list[str] | None = Query(None),
    q: str | None = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List papers within a project with optional filters and sorting (06 §4)."""
    project = repos.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    papers, total = repos.list_papers(
        db=db,
        project_id=project_id,
        status=status,
        q=q,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset,
    )

    items = [to_paper_response(p) for p in papers]
    return ListEnvelope(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/papers",
    response_model=ListEnvelope[PaperResponse],
    summary="List papers (alias)",
)
def list_papers_alias(
    project_id: str = Query(..., description="Project ID"),
    status: list[str] | None = Query(None),
    q: str | None = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Alias for listing papers with project_id as query parameter (06 §4)."""
    return list_project_papers(
        project_id=project_id,
        status=status,
        q=q,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset,
        db=db,
    )


@router.get(
    "/papers/{paper_id}",
    response_model=PaperDetailResponse,
    summary="Get paper details and analysis",
)
def get_paper_details(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """Get single paper by ID with its latest analysis if completed (06 §5)."""
    paper = repos.get_paper(db, paper_id)
    if not paper:
        raise PaperNotFoundError(paper_id)

    analysis_record = repos.get_latest_analysis(db, paper_id)
    if not analysis_record:
        # Dynamically run analysis if paper has chunks
        try:
            from app.services.analysis_service import extract_paper_analysis_heuristically
            chunks = repos.list_chunks_by_paper(db, paper_id)
            if chunks:
                analysis_payload = extract_paper_analysis_heuristically(paper, chunks)
                analysis_record = repos.create_analysis(
                    db=db,
                    analysis_id=new_id("ana"),
                    paper_id=paper_id,
                    prompt_version="1.0.0",
                    llm_model="heuristic-extractor",
                    payload=analysis_payload,
                    status="COMPLETED",
                )
                repos.update_paper_status(db, paper_id, status="ANALYZED")
        except Exception:
            pass

    analysis_payload = analysis_record.payload if analysis_record else None
    analysis_status = analysis_record.status if analysis_record else "NONE"

    return PaperDetailResponse(
        paper=to_paper_response(
            paper,
            has_analysis=analysis_record is not None,
            analysis_status=analysis_status,
        ),
        analysis=analysis_payload,
        analysis_status=analysis_status,
    )


@router.post(
    "/papers/{paper_id}/analyze",
    summary="Trigger analysis for a paper",
)
async def analyze_paper_endpoint(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """Trigger or re-run structured extraction for a paper."""
    paper = repos.get_paper(db, paper_id)
    if not paper:
        raise PaperNotFoundError(paper_id)

    from app.services.analysis_service import analyze_paper
    payload = await analyze_paper(paper_id, db, force_refresh=True)
    return {"paper_id": paper_id, "analysis": payload, "status": "COMPLETED"}



@router.delete(
    "/papers/{paper_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete paper",
)
def delete_paper(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """Delete paper, uploaded file, chunk rows, and vector embeddings (06 §13)."""
    paper = repos.get_paper(db, paper_id)
    if not paper:
        raise PaperNotFoundError(paper_id)

    # 1. Delete vector points in Qdrant
    try:
        vs = get_vector_store()
        vs.delete_by_paper(paper_id)
    except Exception:
        pass

    # 2. Delete file on disk
    delete_paper_file(paper_id)

    # 3. Delete database record (cascades to chunks, analyses, evidence)
    repos.delete_paper(db, paper_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/papers/{paper_id}/chunks",
    response_model=list[ChunkResponse],
    summary="List chunks for a paper",
)
def get_paper_chunks(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """Get all structured chunks for a paper (06 §13)."""
    paper = repos.get_paper(db, paper_id)
    if not paper:
        raise PaperNotFoundError(paper_id)

    chunks = repos.list_chunks_by_paper(db, paper_id)
    return [
        ChunkResponse(
            chunk_id=c.chunk_id,
            paper_id=c.paper_id,
            project_id=c.project_id,
            title=paper.title,
            authors=paper.authors or [],
            year=paper.year,
            section_heading=c.section_heading,
            chunk_type=c.chunk_type,
            page=c.page,
            page_end=c.page_end,
            chunk_index=c.chunk_index,
            text=c.text,
            token_count=c.token_count,
            is_table=c.is_table,
            has_future_cue=c.has_future_cue,
            has_limitation_cue=c.has_limitation_cue,
        )
        for c in chunks
    ]


@router.get(
    "/papers/{paper_id}/file",
    summary="Download original PDF file",
)
def get_paper_file(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """Serve the original uploaded PDF file for in-browser viewing (06 §13)."""
    paper = repos.get_paper(db, paper_id)
    if not paper:
        raise PaperNotFoundError(paper_id)

    path = get_paper_file_path(paper_id)
    if not path or not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Original PDF file not found on disk.",
        )

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=paper.source_filename,
    )
