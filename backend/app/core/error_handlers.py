"""Global exception handlers.

Registered once in `app.main.create_app`. Every handler returns a consistent
error envelope:

    {
        "error": {
            "code": "not_found",
            "message": "Upload 123 was not found",
            "request_id": "..."
        }
    }
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import FlowMindError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_envelope(code: str, message: str, request: Request, **extra: Any) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(request.state, "request_id", None),
            **extra,
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(FlowMindError)
    async def flowmind_error_handler(request: Request, exc: FlowMindError) -> JSONResponse:
        logger.warning(
            "handled_application_error",
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(exc.error_code, exc.message, request),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.info("request_validation_error", errors=exc.errors(), path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_envelope(
                "validation_error",
                "Request validation failed.",
                request,
                details=exc.errors(),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.info(
            "http_exception", status_code=exc.status_code, detail=exc.detail, path=request.url.path
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope("http_error", str(exc.detail), request),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", path=request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_envelope(
                "internal_error",
                "An unexpected error occurred. Our team has been notified.",
                request,
            ),
        )
