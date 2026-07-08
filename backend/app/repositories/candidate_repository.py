from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Candidate
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    """Repository for candidate persistence and lookup operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Candidate)

    async def get_by_email(self, email: str) -> Candidate | None:
        result = await self._session.execute(select(Candidate).where(Candidate.email == email))
        return result.scalar_one_or_none()
