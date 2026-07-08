from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.repositories.factory import RepositoryFactory


async def get_repository_factory(session: Annotated[AsyncSession, Depends(get_db_session)]) -> RepositoryFactory:
    """FastAPI dependency that provides a repository factory for a request-scoped session."""

    return RepositoryFactory(session)


RepositoryFactoryDependency = Annotated[RepositoryFactory, Depends(get_repository_factory)]
