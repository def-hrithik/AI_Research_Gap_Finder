"""
FastAPI application factory — 02 §1.1, 08 §6.
CORS, request-ID middleware, lifespan, router registration.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.core.constants import APP_VERSION
from app.core.ids import new_id
from app.core.logging import ctx_request_id, setup_logging
from app.database.session import init_db
from app.api.errors import register_error_handlers
from app.services.job_service import init_job_runner, shutdown_job_runner, startup_sweep

logger = logging.getLogger("rgf.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events.

    Startup (02 §7, 08 §9.2):
    - Validate settings (fail fast)
    - Initialize DB (create tables)
    - Initialize job runner
    - Mark interrupted jobs as FAILED
    - Create data directories
    - (Later: load embedding model, reranker, connect Qdrant)

    Shutdown:
    - Shut down job runner
    """
    settings = get_settings()

    # Setup logging
    setup_logging(level=settings.log_level, log_format=settings.log_format)
    logger.info("Starting AI Research Gap Finder v%s (%s)", APP_VERSION, settings.environment)

    # Create data directories
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.data_dir, "uploads").mkdir(parents=True, exist_ok=True)

    # Initialize database
    init_db(settings.database_url, settings.data_dir)
    logger.info("Database initialized")

    # Initialize job runner
    init_job_runner(settings.analysis_max_concurrency)

    # Startup sweep: mark interrupted jobs
    swept = startup_sweep()
    if swept:
        logger.info("Startup sweep: %d interrupted jobs marked FAILED", swept)

    logger.info("Application startup complete")

    yield

    # Shutdown
    shutdown_job_runner()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance ready to serve.
    """
    # Validate settings early (fail fast — 08 §9.2)
    settings = get_settings()

    app = FastAPI(
        title="AI Research Gap Finder",
        version=APP_VERSION,
        description="Evidence-grounded academic literature analysis platform",
        lifespan=lifespan,
    )

    # --- CORS --- (06 §1, 08 §10)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_origin_regex=settings.cors_origin_regex or None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "Retry-After", "Location"],
    )

    # --- Request-ID middleware --- (06 §1)
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next) -> Response:
        """Assign/echo X-Request-ID on every request (06 §1)."""
        req_id = request.headers.get("X-Request-ID")
        if not req_id or len(req_id) > 64:
            req_id = new_id("req")
        ctx_request_id.set(req_id)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response

    # --- Error handlers ---
    register_error_handlers(app)

    # --- Routers ---
    from app.api.health import router as health_router
    from app.api.projects import router as projects_router
    from app.api.jobs import router as jobs_router
    from app.api.papers import router as papers_router
    from app.api.search import router as search_router
    from app.api.research import router as research_router

    app.include_router(health_router, prefix="/api")
    app.include_router(projects_router, prefix="/api")
    app.include_router(jobs_router, prefix="/api")
    app.include_router(papers_router, prefix="/api")
    app.include_router(search_router, prefix="/api")
    app.include_router(research_router, prefix="/api")

    return app


# The app instance used by uvicorn
app = create_app()
