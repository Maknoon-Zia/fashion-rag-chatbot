"""Application errors and the handlers that turn them into safe JSON responses.

Every error body looks like: {"detail": "<human message>", "code": "<machine code>", ...}
Stack traces and internal messages are never returned to clients.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class AppError(Exception):
    """An expected error with a safe, user-facing message."""

    def __init__(self, status_code: int, code: str, message: str, **extra: object) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.extra = extra


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found.") -> None:
        super().__init__(404, "not_found", message)


class UpstreamError(AppError):
    """An external dependency (embeddings, Qdrant, LLM) failed."""

    def __init__(self, code: str, message: str, **extra: object) -> None:
        super().__init__(503, code, message, **extra)


def _json(status: int, body: dict, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status, content=body, headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return _json(exc.status_code, {"detail": exc.message, "code": exc.code, **exc.extra})

    @app.exception_handler(HTTPException)
    async def _http_error(_: Request, exc: HTTPException) -> JSONResponse:
        return _json(exc.status_code, {"detail": str(exc.detail), "code": "http_error"}, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for err in exc.errors():
            loc = [str(p) for p in err.get("loc", ()) if p not in ("body", "query", "path")]
            msg = str(err.get("msg", "Invalid value")).removeprefix("Value error, ")
            errors.append({"field": ".".join(loc), "message": msg})
        return _json(
            422,
            {"detail": "Please check the highlighted fields.", "code": "validation_error", "errors": errors},
        )

    @app.exception_handler(PyMongoError)
    async def _mongo_error(_: Request, exc: PyMongoError) -> JSONResponse:
        logger.error("MongoDB error: %s", type(exc).__name__)
        return _json(
            503, {"detail": "The database is temporarily unavailable. Please try again.", "code": "database_unavailable"}
        )

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", type(exc).__name__)  # traceback stays in server logs
        return _json(500, {"detail": "Something went wrong on our side.", "code": "internal_error"})
