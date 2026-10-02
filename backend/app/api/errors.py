"""
API error handlers — 08 §7.
Maps AppError → structured JSON envelope. Never leaks internals.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import AppError
from app.core.logging import ctx_request_id

logger = logging.getLogger("rgf.api.errors")


def register_error_handlers(app: FastAPI) -> None:
    """Register exception handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Handle known application errors → structured envelope (06 §1.2)."""
        request_id = ctx_request_id.get() or "unknown"
        logger.warning(
            "AppError: %s %s (request_id=%s)", exc.code, exc.message, request_id,
            extra={"event": "app_error", "code": exc.code},
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic/FastAPI validation errors → 422 VALIDATION_ERROR."""
        request_id = ctx_request_id.get() or "unknown"
        fields = []
        for err in exc.errors():
            fields.append({
                "loc": list(err.get("loc", [])),
                "msg": err.get("msg", ""),
            })
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": {"fields": fields},
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unhandled exceptions → 500 INTERNAL_ERROR.

        Full traceback goes to server logs only (08 §7).
        """
        request_id = ctx_request_id.get() or "unknown"
        logger.exception(
            "Unhandled exception (request_id=%s)", request_id,
            extra={"event": "internal_error"},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred.",
                    "details": {},
                    "request_id": request_id,
                }
            },
        )
