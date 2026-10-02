"""
Application errors — 08 §7, 06 §1.4.
Single exception root with structured error envelope.
"""


class AppError(Exception):
    """Base application error. All service-layer exceptions inherit from this.

    Attributes:
        code: Machine-readable error code from the catalog (06 §1.4).
        http_status: Corresponding HTTP status code.
        message: Human-safe message (never stack traces, paths, SQL, prompts, or keys).
        details: Optional structured context.
        retryable: Whether the client should retry.
    """

    def __init__(
        self,
        code: str,
        http_status: int = 500,
        message: str = "An internal error occurred.",
        details: dict | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.message = message
        self.details = details or {}
        self.retryable = retryable


# --- Not Found (404) ---

class NotFoundError(AppError):
    """Resource not found — 06 §1.3."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        super().__init__(code=code, http_status=404, message=message, details=details)


class ProjectNotFoundError(NotFoundError):
    def __init__(self, project_id: str) -> None:
        super().__init__(
            code="PROJECT_NOT_FOUND",
            message=f"Project '{project_id}' not found.",
            details={"project_id": project_id},
        )


class PaperNotFoundError(NotFoundError):
    def __init__(self, paper_id: str) -> None:
        super().__init__(
            code="PAPER_NOT_FOUND",
            message=f"Paper '{paper_id}' not found.",
            details={"paper_id": paper_id},
        )


class ChunkNotFoundError(NotFoundError):
    def __init__(self, chunk_id: str) -> None:
        super().__init__(
            code="CHUNK_NOT_FOUND",
            message=f"Chunk '{chunk_id}' not found.",
            details={"chunk_id": chunk_id},
        )


class GapNotFoundError(NotFoundError):
    def __init__(self, gap_id: str) -> None:
        super().__init__(
            code="GAP_NOT_FOUND",
            message=f"Gap '{gap_id}' not found.",
            details={"gap_id": gap_id},
        )


class RunNotFoundError(NotFoundError):
    def __init__(self, run_id: str) -> None:
        super().__init__(
            code="RUN_NOT_FOUND",
            message=f"Run '{run_id}' not found.",
            details={"run_id": run_id},
        )


class ReportNotFoundError(NotFoundError):
    def __init__(self, report_id: str) -> None:
        super().__init__(
            code="REPORT_NOT_FOUND",
            message=f"Report '{report_id}' not found.",
            details={"report_id": report_id},
        )


class JobNotFoundError(NotFoundError):
    def __init__(self, job_id: str) -> None:
        super().__init__(
            code="JOB_NOT_FOUND",
            message=f"Job '{job_id}' not found.",
            details={"job_id": job_id},
        )


# --- Conflict (409) ---

class ConflictError(AppError):
    """State conflict — 06 §1.3."""

    def __init__(
        self, code: str, message: str, details: dict | None = None, retryable: bool = False
    ) -> None:
        super().__init__(
            code=code, http_status=409, message=message, details=details, retryable=retryable
        )


class DuplicatePaperError(ConflictError):
    def __init__(self, existing_paper_id: str) -> None:
        super().__init__(
            code="DUPLICATE_PAPER",
            message="This PDF already exists in the project.",
            details={"existing_paper_id": existing_paper_id},
        )


class ProjectPaperLimitError(ConflictError):
    def __init__(self, limit: int) -> None:
        super().__init__(
            code="PROJECT_PAPER_LIMIT",
            message=f"Project has reached the maximum of {limit} papers.",
            details={"limit": limit},
        )


class PapersNotReadyError(ConflictError):
    def __init__(self, paper_ids: list[str]) -> None:
        super().__init__(
            code="PAPERS_NOT_READY",
            message="Some papers are still being processed or have failed.",
            details={"paper_ids": paper_ids},
            retryable=True,
        )


class NoIndexedPapersError(ConflictError):
    def __init__(self) -> None:
        super().__init__(
            code="NO_INDEXED_PAPERS",
            message="This project has no indexed papers available for search or analysis.",
        )


class AnalysisInProgressError(ConflictError):
    def __init__(self) -> None:
        super().__init__(
            code="ANALYSIS_IN_PROGRESS",
            message="An analysis is already in progress for this paper.",
            retryable=True,
        )


class RunNotCompleteError(ConflictError):
    def __init__(self, run_id: str) -> None:
        super().__init__(
            code="RUN_NOT_COMPLETE",
            message="The referenced run has not completed yet.",
            details={"run_id": run_id},
            retryable=True,
        )


# --- Validation (422) ---

class ValidationError(AppError):
    """Domain validation failure — 06 §1.3."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            code="VALIDATION_ERROR", http_status=422, message=message, details=details
        )


class PaperNotInProjectError(AppError):
    def __init__(self, paper_ids: list[str]) -> None:
        super().__init__(
            code="PAPER_NOT_IN_PROJECT",
            http_status=422,
            message="One or more papers do not belong to this project.",
            details={"paper_ids": paper_ids},
        )


# --- Upload (413, 415) ---

class FileTooLargeError(AppError):
    def __init__(self, max_mb: int) -> None:
        super().__init__(
            code="FILE_TOO_LARGE",
            http_status=413,
            message=f"File exceeds the maximum allowed size of {max_mb} MB.",
            details={"max_mb": max_mb},
        )


class UnsupportedMediaTypeError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="UNSUPPORTED_MEDIA_TYPE",
            http_status=415,
            message="Only PDF files are accepted.",
        )


# --- Ingest errors (used in job error field) ---

class IngestError(AppError):
    """PDF processing failure — 06 §1.4."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        super().__init__(code=code, http_status=500, message=message, details=details)


# --- LLM errors ---

class LLMError(AppError):
    """LLM provider failure — 06 §1.4."""

    def __init__(
        self, code: str, message: str, details: dict | None = None, retryable: bool = True
    ) -> None:
        super().__init__(
            code=code,
            http_status=502 if code != "LLM_TIMEOUT" else 504,
            message=message,
            details=details,
            retryable=retryable,
        )


# --- Infrastructure ---

class VectorStoreError(AppError):
    def __init__(self, message: str = "Vector store is unavailable.") -> None:
        super().__init__(
            code="VECTOR_STORE_UNAVAILABLE",
            http_status=503,
            message=message,
            retryable=True,
        )


class ModelsNotReadyError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code="MODELS_NOT_READY",
            http_status=503,
            message="Embedding or reranker models are still loading.",
            retryable=True,
        )
