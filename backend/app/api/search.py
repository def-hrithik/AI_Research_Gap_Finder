"""
Search API endpoints — 06 §8.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import ProjectNotFoundError
from app.database import repos
from app.schemas.retrieval import SearchRequest, SearchResponse
from app.services.search_service import execute_search

router = APIRouter(tags=["search"])


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Hybrid literature search and grounded answer",
)
async def search_endpoint(
    req: SearchRequest,
    db: Session = Depends(get_db),
):
    """Execute dense + BM25 hybrid search with intent prior and grounded answer (06 §8)."""
    project = repos.get_project(db, req.project_id)
    if not project:
        raise ProjectNotFoundError(req.project_id)

    return await execute_search(
        project_id=req.project_id,
        query=req.query,
        db=db,
        filters=req.filters,
        generate_answer=req.generate_answer,
        top_k=req.top_k,
    )
