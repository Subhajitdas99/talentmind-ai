from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("", response_model=dict[str, str])
async def health_check(request: Request) -> dict[str, str]:
    """Return service health information for monitoring and readiness checks."""

    settings = request.app.state.settings
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
