"""
Structured logging — 08 §8.
JSON formatter for production, console for development.
Context vars carry request_id, job_id, run_id, project_id, paper_id.
"""

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

# Context variables — injected by middleware and job runner (08 §8)
ctx_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
ctx_job_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "job_id", default=None
)
ctx_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "run_id", default=None
)
ctx_project_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "project_id", default=None
)
ctx_paper_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "paper_id", default=None
)


class ContextFilter(logging.Filter):
    """Inject context vars into every log record (08 §8)."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = ctx_request_id.get()  # type: ignore[attr-defined]
        record.job_id = ctx_job_id.get()  # type: ignore[attr-defined]
        record.run_id = ctx_run_id.get()  # type: ignore[attr-defined]
        record.project_id = ctx_project_id.get()  # type: ignore[attr-defined]
        record.paper_id = ctx_paper_id.get()  # type: ignore[attr-defined]
        return True


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production (08 §8)."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context vars if present
        for attr in ("request_id", "job_id", "run_id", "project_id", "paper_id"):
            val = getattr(record, attr, None)
            if val is not None:
                log_entry[attr] = val

        # Add event-specific fields
        if hasattr(record, "event"):
            log_entry["event"] = record.event  # type: ignore[attr-defined]
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms  # type: ignore[attr-defined]

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(level: str = "INFO", log_format: str = "console") -> None:
    """Configure root logger with appropriate formatter (08 §8).

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        log_format: 'console' for dev, 'json' for production.
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())

    if log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "req=%(request_id)s job=%(job_id)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    root.addHandler(handler)

    # Quiet noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger.

    Args:
        name: Module or component name (e.g. 'ingestion.pdf_parser').

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"rgf.{name}")
