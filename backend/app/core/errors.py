"""Structured application errors and FastAPI exception handlers.

Clients always receive {error, code, detail}; stack traces never leak.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error with an HTTP status and stable code."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"

    def __init__(self, detail: str, *, code: str | None = None, status_code: int | None = None):
        self.detail = detail
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        super().__init__(detail)


class AuthError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


def _body(error: str, code: str, detail) -> dict:
    return {"error": error, "code": code, "detail": detail}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.__class__.__name__, exc.code, exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_body("ValidationError", "invalid_input", exc.errors()),
        )
