import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import Settings
from app.database.session import build_engine
from app.presentation.accounts import router as accounts_router
from app.presentation.errors import ErrorResponse, install_errors
from app.presentation.health import router
from app.presentation.productivity import router as productivity_router
from app.presentation.tasks import router as tasks_router


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    request_logger = logging.getLogger("devtreck.requests")
    request_logger.setLevel(logging.INFO)
    if not request_logger.handlers:
        request_logger.addHandler(logging.StreamHandler())

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        engine = (
            build_engine(config.database_url.get_secret_value()) if config.database_url else None
        )
        application.state.engine = engine
        try:
            yield
        finally:
            if engine is not None:
                engine.dispose()

    application = FastAPI(
        lifespan=lifespan,
        responses={
            code: {"model": ErrorResponse} for code in (400, 401, 403, 404, 409, 422, 429, 500, 503)
        },
        title="Devtreck API",
        version="0.1.0",
        debug=config.app_debug,
        docs_url=None if config.app_env == "production" else "/docs",
        redoc_url=None,
        openapi_url=None if config.app_env == "production" else "/openapi.json",
    )
    application.state.settings = config
    application.include_router(accounts_router)
    application.include_router(tasks_router)
    application.include_router(productivity_router)
    install_errors(application)

    @application.middleware("http")
    async def correlate(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.request_id = str(uuid4())
        started = perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        logging.getLogger("devtreck.requests").info(
            json.dumps(
                {
                    "event": "request",
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "status": response.status_code,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                }
            )
        )
        return response

    application.include_router(router)
    return application


app = create_app()
