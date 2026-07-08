from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import DatabaseFactory
from app.database.session import SessionManager, get_db_session


@lru_cache(maxsize=1)
def get_database_factory(database_url: str | None = None) -> DatabaseFactory:
    """Return a cached database factory for the current process."""

    return DatabaseFactory(database_url=database_url)


@lru_cache(maxsize=1)
def get_session_manager(database_url: str | None = None) -> SessionManager:
    """Return a cached session manager for the current process."""

    return SessionManager(database_url=database_url)


DBSessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
