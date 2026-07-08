from __future__ import annotations

from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class RepositoryError(Exception):
    """Raised when a repository operation fails for a domain-level reason."""


class BaseRepository(Generic[ModelType]):
    """Generic async repository providing common CRUD operations."""

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self._session = session
        self._model = model

    def _select(self) -> Select[tuple[ModelType]]:
        return select(self._model)

    def _apply_filters(self, statement: Select[tuple[ModelType]], filters: dict[str, Any] | None = None) -> Select[tuple[ModelType]]:
        if not filters:
            return statement

        for key, value in filters.items():
            if value is None:
                continue
            if isinstance(value, (list, tuple, set)):
                statement = statement.where(getattr(self._model, key).in_(value))
            else:
                statement = statement.where(getattr(self._model, key) == value)
        return statement

    def _apply_sorting(
        self,
        statement: Select[tuple[ModelType]],
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> Select[tuple[ModelType]]:
        if not sort_by:
            return statement
        column = getattr(self._model, sort_by)
        return statement.order_by(column.desc() if sort_desc else column.asc())

    async def get_by_id(self, id: Any) -> ModelType | None:
        result = await self._session.execute(self._select().where(self._model.id == id))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> list[ModelType]:
        statement = self._select()
        statement = self._apply_filters(statement, filters)
        statement = self._apply_sorting(statement, sort_by=sort_by, sort_desc=sort_desc)
        result = await self._session.execute(statement.offset(offset).limit(limit))
        return list(result.scalars().all())

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        statement = select(self._model)
        statement = self._apply_filters(statement, filters)
        result = await self._session.execute(select(statement.subquery().c.id).count())
        return int(result.scalar_one())

    async def create(self, **data: Any) -> ModelType:
        instance = self._model(**data)
        try:
            self._session.add(instance)
            await self._session.flush()
            await self._session.refresh(instance)
        except IntegrityError as exc:
            await self._session.rollback()
            raise RepositoryError("Failed to create record") from exc
        except SQLAlchemyError as exc:
            await self._session.rollback()
            raise RepositoryError("Database error while creating record") from exc
        return instance

    async def update(self, instance: ModelType, **data: Any) -> ModelType:
        for key, value in data.items():
            setattr(instance, key, value)
        try:
            self._session.add(instance)
            await self._session.flush()
            await self._session.refresh(instance)
        except IntegrityError as exc:
            await self._session.rollback()
            raise RepositoryError("Failed to update record") from exc
        except SQLAlchemyError as exc:
            await self._session.rollback()
            raise RepositoryError("Database error while updating record") from exc
        return instance

    async def delete(self, instance: ModelType) -> None:
        try:
            await self._session.delete(instance)
            await self._session.flush()
        except SQLAlchemyError as exc:
            await self._session.rollback()
            raise RepositoryError("Database error while deleting record") from exc

    async def soft_delete(self, instance: ModelType) -> None:
        if hasattr(instance, "is_deleted"):
            setattr(instance, "is_deleted", True)
            setattr(instance, "deleted_at", None)
        try:
            self._session.add(instance)
            await self._session.flush()
        except SQLAlchemyError as exc:
            await self._session.rollback()
            raise RepositoryError("Database error while soft deleting record") from exc

    @asynccontextmanager
    async def transaction(self) -> Any:
        try:
            async with self._session.begin():
                yield self._session
        except SQLAlchemyError as exc:
            raise RepositoryError("Database transaction failed") from exc
