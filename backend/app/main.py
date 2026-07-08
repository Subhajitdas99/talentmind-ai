from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, log_request_middleware, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown hooks for the FastAPI application."""

    settings: Settings = app.state.settings
    setup_logging(settings)
    logger.info("Starting TalentMind AI API in {} mode", settings.environment)
    try:
        yield
    finally:
        logger.info("Shutting down TalentMind AI API")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application instance."""

    settings = settings or get_settings()
    settings = settings if isinstance(settings, Settings) else Settings(**settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-grade AI recruitment platform for candidate discovery, "
            "ranking, and recruiter workflows."
        ),
        docs_url=settings.docs_url if settings.is_development else None,
        redoc_url=settings.redoc_url if settings.is_development else None,
        openapi_url=settings.openapi_url if settings.is_development else None,
        contact={"name": "TalentMind AI Engineering", "email": "engineering@talentmind.ai"},
        license_info={"name": "Proprietary", "url": "https://talentmind.ai/license"},
        lifespan=lifespan,
    )
    app.state.settings = settings

    register_exception_handlers(app, logger)

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)

    @app.get("/", tags=["health"], summary="Service root", description="Returns a simple health indicator for the API")
    async def root() -> dict[str, str]:
        return {"message": f"{settings.app_name} API is running"}

    @app.get("/health", tags=["health"], summary="Health check", description="Returns the service health payload")
    async def healthcheck() -> dict[str, Any]:
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

    try:
        from app.api.v1.api import api_router
    except ImportError:
        logger.debug("API router is not available yet; skipping inclusion")
    else:
        app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
