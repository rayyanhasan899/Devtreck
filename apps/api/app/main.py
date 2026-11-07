from fastapi import FastAPI

from app.core.config import Settings
from app.presentation.health import router


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    application = FastAPI(
        title="Devtreck API",
        version="0.1.0",
        debug=config.app_debug,
        docs_url=None if config.app_env == "production" else "/docs",
        redoc_url=None,
        openapi_url=None if config.app_env == "production" else "/openapi.json",
    )
    application.include_router(router)
    return application


app = create_app()
