import json
import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from app.domain.errors import ApplicationError, ConflictError, NotFoundError, UnauthorizedError


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: list[str] = []


class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: str


logger = logging.getLogger("devtreck.requests")


def install_errors(app: FastAPI) -> None:
    def response(request: Request, status: int, code: str, message: str) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        return JSONResponse(
            status_code=status,
            content={"error": {"code": code, "message": message}, "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(ApplicationError)
    async def application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        if isinstance(exc, UnauthorizedError):
            return response(
                request, 401, "unauthorized", "Authentication or reauthentication required"
            )
        if isinstance(exc, NotFoundError):
            return response(request, 404, "not_found", "Resource not found")
        if isinstance(exc, ConflictError):
            return response(request, 409, "conflict", "Operation conflicts with current state")
        return response(request, 503, "unavailable", "Service temporarily unavailable")

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return response(request, 503, "unavailable", "Service temporarily unavailable")

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Allowlisted field names only; never include submitted input or validator context.
        fields = [
            ".".join(
                str(part)
                for part in error["loc"]
                if isinstance(part, int)
                or part
                in {
                    "body",
                    "email",
                    "name",
                    "password",
                    "new_password",
                    "current_password",
                    "theme",
                    "time_zone",
                    "confirm",
                    "title",
                    "description",
                    "status",
                    "task_type",
                    "priority",
                    "category_id",
                    "due_date",
                    "due_at",
                    "estimated_minutes",
                    "limit",
                    "offset",
                    "view",
                    "search",
                    "sort",
                    "descending",
                    "overdue",
                    "task_id",
                    "path",
                    "query",
                }
            )
            for error in exc.errors()
        ]
        request_id = getattr(request.state, "request_id", str(uuid4()))
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Invalid request data",
                    "fields": fields,
                },
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return response(request, exc.status_code, "http_error", "Request could not be completed")

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            json.dumps(
                {
                    "event": "request_failed",
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "error_type": type(exc).__name__,
                }
            ),
        )
        return response(request, 500, "internal_error", "Unexpected server error")
