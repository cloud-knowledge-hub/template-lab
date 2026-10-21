import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Settings, get_settings
from app.logging_config import setup_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings) -> FastAPI:
    """Create a FastAPI application configured with the supplied settings."""

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        setup_logging(settings)
        logger.info(
            "Starting up %s in %s mode.",
            settings.app_name,
            settings.environment,
        )

        try:
            yield
        finally:
            logger.info("Shutting down %s", settings.app_name)

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """Return basic service status and active environment."""

        return {
            "status": "ok",
            "environment": settings.environment,
        }

    return app


app = create_app(get_settings())
