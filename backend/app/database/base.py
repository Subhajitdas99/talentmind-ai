from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.core.logging import get_logger

from app.core.config import get_settings


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower() + "s"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


logger = get_logger(__name__)


class DatabaseFactory:
    """Factory responsible for creating and caching async SQLAlchemy resources."""

    def __init__(self, database_url: str | None = None) -> None:
        self._database_url = database_url or get_settings().database_url
        self._engine: Any = None
        self._session_factory: Any = None

    @property
    def engine(self) -> Any:
        """Lazily create the async SQLAlchemy engine with pooling enabled."""

        if self._engine is None:
            logger.debug("Creating async database engine for {}", self._database_url.split("@")[-1])
            self._engine = create_async_engine(
                self._database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=1800,
                pool_size=10,
                max_overflow=20,
            )
        return self._engine

    @property
    def session_factory(self) -> Any:
        """Create a configured async session factory for dependency injection."""

        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        return self._session_factory

    async def dispose(self) -> None:
        """Dispose the engine and release pooled connections."""

        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.debug("Async database engine disposed")
