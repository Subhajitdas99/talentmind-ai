from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import Request
from loguru import logger as loguru_logger

from app.core.config import Settings, get_settings


class InterceptHandler:
    """Bridge Loguru with standard library logging if needed by third-party libraries."""

    def emit(self, record: Any) -> None:  # pragma: no cover - simple bridge
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        message = record.getMessage()
        if record.exc_info:
            message = f"{message} | {record.exc_info[1]}"

        loguru_logger.opt(depth=6, exception=record.exc_info).log(level, message)


def _json_serializer(message: Any) -> str:
    """Serialize log records as JSON for structured observability."""

    record = message.record
    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "process": record["process"].id,
        "request_id": record["extra"].get("request_id"),
    }
    return json.dumps(payload)


def setup_logging(settings: Settings | None = None) -> None:
    """Configure Loguru with console output, JSON file logs, daily rotation, and retention."""

    settings = settings or get_settings()
    loguru_logger.remove()

    loguru_logger.add(
        sink="stdout",
        level=settings.log_level.upper(),
        format=lambda message: _json_serializer(message),
        enqueue=True,
        backtrace=settings.debug,
        diagnose=settings.debug,
    )

    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        loguru_logger.add(
            sink=str(log_path),
            level=settings.log_level.upper(),
            format=lambda message: _json_serializer(message),
            enqueue=True,
            rotation="00:00",
            retention="30 days",
            compression="zip",
            backtrace=settings.debug,
            diagnose=settings.debug,
        )


def get_logger(name: str | None = None) -> Any:
    """Return a Loguru logger bound to a module name."""

    return loguru_logger.bind(name=name or "app")


def get_request_id() -> str:
    """Return an existing request ID from context or generate a new one."""

    return str(uuid.uuid4())


async def log_request_middleware(request: Request, call_next: Any) -> Any:
    """Middleware that attaches a request ID and logs request and response metrics."""

    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    logger = get_logger("api.request").bind(request_id=request_id)

    start_time = time.perf_counter()
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        query_params=str(request.url.query),
    )

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response
    except Exception as exc:  # pragma: no cover - exercised in runtime
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.exception(
            "request_failed",
            method=request.method,
            path=request.url.path,
            duration_ms=round(duration_ms, 2),
            error=str(exc),
        )
        raise
