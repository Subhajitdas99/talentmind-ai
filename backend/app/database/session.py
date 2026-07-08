from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.database.base import DatabaseFactory

logger = get_logger(__name__)


class SessionManager:
    """Session manager that provides async sessions and health checks."""

    def __init__(self, database_url: str | None = None) -> None:
        self._factory = DatabaseFactory(database_url=database_url)

    @property
    def factory(self) -> DatabaseFactory:
        return self._factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield an async session for dependency injection with explicit lifecycle management."""

        async with self._factory.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """Verify that the database is reachable with a lightweight query."""

        for attempt in range(3):
            try:
                async with self._factory.engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
                return True
            except OperationalError:
                if attempt == 2:
                    raise
        return False


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""

    session_manager = SessionManager()
    async for session in session_manager.get_session():
        yield session


# Import text here to avoid circular import issues during SQLAlchemy execution.
from sqlalchemy import text  # noqa: E402
