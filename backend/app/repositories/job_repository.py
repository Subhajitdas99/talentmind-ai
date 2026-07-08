from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Repository for job persistence and lookup operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Job)

    async def get_by_title(self, title: str) -> Job | None:
        result = await self._session.execute(select(Job).where(Job.title == title))
        return result.scalar_one_or_none()
