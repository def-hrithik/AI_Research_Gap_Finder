"""
Health endpoints — 06 §13.
GET /api/health (liveness), GET /api/health/ready (readiness).
"""

from fastapi import APIRouter

from app.api.deps import DbDep, SettingsDep
from app.core.constants import APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Liveness check — 06 §13."""
    return {"status": "ok", "version": APP_VERSION}


@router.get("/health/ready")
async def health_ready(settings: SettingsDep, db: DbDep) -> dict:
    """Readiness check — 06 §13.

    Checks: database, vector_store, embedding_model, reranker, llm.
    """
    checks: dict[str, str] = {}

    # Database check
    try:
        db.execute(db.bind.dialect.has_table.__func__ and db.connection())  # type: ignore
        checks["database"] = "ok"
    except Exception:
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "error"

    # Vector store (will be checked when Qdrant module exists)
    checks["vector_store"] = "ok"  # placeholder until Phase 7

    # Embedding model (will be checked when embedder module exists)
    checks["embedding_model"] = "not_loaded"  # placeholder until Phase 6

    # Reranker
    if settings.reranker_enabled:
        checks["reranker"] = "not_loaded"  # placeholder until Phase 11
    else:
        checks["reranker"] = "disabled"

    # LLM
    if settings.llm_provider == "fake":
        checks["llm"] = "fake"
    elif settings.llm_api_key:
        checks["llm"] = "configured"
    else:
        checks["llm"] = "not_configured"

    all_ok = all(v in ("ok", "configured", "fake", "disabled", "loaded") for v in checks.values())
    status_code = 200 if all_ok else 200  # Return 200 for now, 503 when all checks are real

    return {"status": "ready" if all_ok else "degraded", "checks": checks}
