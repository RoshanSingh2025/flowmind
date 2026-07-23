"""Application-level exceptions.

Services and repositories raise these instead of HTTPException so business logic
stays framework-agnostic. The global exception handlers (see
`app.core.error_handlers`) translate them into HTTP responses at the edge.
"""

from __future__ import annotations


class FlowMindError(Exception):
    """Base class for all application-raised errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, *, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if error_code:
            self.error_code = error_code


class NotFoundError(FlowMindError):
    status_code = 404
    error_code = "not_found"


class ValidationError(FlowMindError):
    status_code = 422
    error_code = "validation_error"


class ConflictError(FlowMindError):
    status_code = 409
    error_code = "conflict"


class UnauthorizedError(FlowMindError):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(FlowMindError):
    status_code = 403
    error_code = "forbidden"


class UnsupportedFileTypeError(ValidationError):
    error_code = "unsupported_file_type"


class FileTooLargeError(ValidationError):
    error_code = "file_too_large"
